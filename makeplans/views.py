import os

from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from django.urls import reverse

from .models import Student
from .forms import StudentForm, GptForm, RagForm

import openai
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback

from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient

from lzstring import LZString


def index(request):
    student_list = Student.objects.order_by("-record_date")
    context = {"student_list": student_list}
    return render(request, "makeplans/index.html", context)


def record(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            Student.objects.create(
                student_name=form.cleaned_data['student_name'],
                record_date=form.cleaned_data['record_date'],
                content=form.cleaned_data['content']
            )
            message = "記録を追加しました"
            form = StudentForm()
            context = {
                "message": message,
                "form": form,
                    }
        return render(request, "makeplans/record.html", context)
    else:
        form = StudentForm()
        context = {"form": form}
    return render(request, "makeplans/record.html", context)


def gpt(request):
    if request.method == 'POST':
        form = GptForm(request.POST)
        selected_student = request.POST.get('student_name')
        if selected_student:
            selected_students_list = get_list_or_404(
                Student.objects.filter(student_name=selected_student).order_by("record_date")
                )
            
            #日案をまとめたリストを作成
            content_set = []
            if selected_students_list:
                for student in selected_students_list:
                    formatted_date = student.record_date.strftime('%Y年%m月%d日')
                    content_set.append([formatted_date, student.content])
                
                #リストを参考に月案作成
                os.environ["OPENAI_API_KEY"] = "" #APIキーを入力

                #プロンプトを定義
                sentense1 = """

下記にする質問の構成は以下の通りです。

**質問の構成** 
"""

                sentense2 = "次に挙げる乳児の個別記録のリストを参照して、次の月の指導計画を作成してください。なお個別記録のリストは['記録した日付','乳児の出来事']が格納されています。\n" + "乳児の名前：" + selected_student + "\n" + "個別記録：\n" + str(content_set) + "\n **** \n"

                sentense3 ="""
あなたは、質問にある個別記録を基に「月のねらい」、「先月末の子供の姿」、「活動内容」、「保育士が配慮すべき事項」の4つを作成します。
月のねらい: 個別記録に記載されている先月末の出来事をもとに、次の月の目標を立てる。箇条書きで4つ作成する。
先月末の子供の姿: 個別記録に記載されている先月末の出来事をもとに、1カ月の出来事をまとめる。実際の出来事を引用しつつ100文字以上で作成する。
活動内容: 個別記録に記載されている先月末の出来事や月のねらいをもとに、次の月の目標に対する具体的な活動目標を立てる。箇条書きで5つ以上作成する。
保育士が配慮すべき事項: 上記の活動目標に対して、保育士が健康面や安全面で注意すべき事項をまとめる。箇条書きで3つ作成する。

**アウトプットのテンプレート**
 #前置きの言葉はいらないので、以下から始めてください
1. 月のねらい：
2. 先月末の子供の姿：
3. 活動内容：
4. 保育士が配慮すべき事項：
****

**質問文**
"""
                
                sentense4 = selected_student + "の個別記録を参照して、次の月の指導計画を作成して下さい。\n****"
                
                prompt = sentense1 + sentense2 + sentense3 + sentense4
                
                #ターミナル上にChatGPTへのプロンプトを表示させる
                print("============(ChatGPTへのプロンプト)============\n",prompt,"\n========================")

                # ChatGPT
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "あなたは保育士で乳児の指導計画を作成するスペシャリストです。文末は「です」や「ます」を付けて応答してください。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        },
                    ],
                )

                #ChatGPTの出力結果
                monthly_plan = response.choices[0].message.content 
                token_size = response.usage
                print("============(token量)============\n",token_size)
            #GPT処理ここまで

                #URLパラメータのリダイレクトのための、GPT出力の圧縮
                monthly_plan_compressed = LZString().compressToEncodedURIComponent(monthly_plan) 

        return redirect(reverse('makeplans:rag', kwargs={'selected_student':selected_student, 'monthly_plan_compressed':monthly_plan_compressed}))
    else:
        form = GptForm()
        return render(request, "makeplans/monthly.html", {"form": form})
    

def rag(request, monthly_plan_compressed, selected_student):
    form = GptForm()
    monthly_plan = LZString().decompressFromEncodedURIComponent(monthly_plan_compressed)

    if request.method == 'POST':
        rag_form = RagForm(request.POST)
        rag_query = request.POST.get('rag_query')
        
        #RAGの処理
        # Qdrantのベクトルストアを設定
        # 初期化
        os.environ["OPENAI_API_KEY"] = "" #APIキーを入力
        embeddings = OpenAIEmbeddings()
        client = QdrantClient("localhost", port=6333)

        vector_store = Qdrant(
            client=client,
            collection_name="ChildCare_PdfData",
            embeddings=embeddings
        )

        # リトリーバーの設定
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        rag_ans=""

        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, verbose=True)
        llm_prompt_template = """
あなたは乳児の指導を行う保育士です。
次のコンテクストと質問トピックに基づいて、該当するトピックにおける乳児の事故や危険のもととなり得るポイントを事例を交つつ教えて下さい。
  コンテクスト：{context}
  質問トピック：{question}

ただし、アウトプットの構成は以下の通りです。
===
 #前置きの言葉はいらないので、以下から始めてください
-事故や危険の事例
-事前の予防策と保育士が注意すべき点
 #これを2つ出力する。
===

"""
        llm_prompt = ChatPromptTemplate.from_template(llm_prompt_template)
        print("============(ChatGPTへのプロンプト)============\n",llm_prompt,"\n========================")

        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | llm_prompt
            | llm
            | StrOutputParser()
            )
        with get_openai_callback() as cb:
            rag_ans = rag_chain.invoke(rag_query)
            print("============(token量)============\n", cb)

            references = retriever.get_relevant_documents(rag_query)
            print("該当する個別記録：", "\n==========\n")
            for doc in references:
                print(doc.page_content,"\n=============\n")
            
            
        context = {
            "rag_form": rag_form,
            "monthly_plan": monthly_plan,
            "form": form,
            "selected_student": selected_student,
            "rag_ans": rag_ans,
                }
        return render(request, "makeplans/monthly.html", context) 
    else:
        rag_form = RagForm()

        context = {
            "selected_student": selected_student,
            "form": form,
            "monthly_plan": monthly_plan,
            "rag_form": rag_form
                }
        return render(request, "makeplans/monthly.html", context)