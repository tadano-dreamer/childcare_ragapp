from lzstring import LZString

# 圧縮する
def compress_to_encoded_uri_component(input_string):
    lz = LZString()
    return lz.compressToEncodedURIComponent(input_string)

# 解凍する
def decompress_from_encoded_uri_component(compressed_string):
    lz = LZString()
    return lz.decompressFromEncodedURIComponent(compressed_string)

# 使用例
original_string = "1. 月のねらい： - 先月末の出来事を振り返り、コミュニケーション能力を育てる。 - 社会性を促進するための活動を取り入れる。 - 視覚や聴覚を刺激する活動を通して感性を養う。 - 自己表現を促進するための機会を提供する。 2. 先月末の子供の姿： 先月末、K児は笑顔で周囲の子供たちと積極的に関わり、好奇心旺盛に新しいおもちゃで遊んでいました。身体能力も向上し、はしごを登ることに挑戦する姿が見られました。 3. 活動内容： - 新しいおもちゃを導入し、友達との共同遊びを促す。 - 音楽に合わせて身体を動かすリズム遊びを行う。 - 絵本の読み聞かせを通じて言葉の理解を深める。 - 様々な色や形を使った手作りおもちゃで感覚遊びを提供する。 - 鏡を使った身体の反射遊びを通じて自己認識を促す。 4. 保育士が配慮すべき事項： - 新しいおもちゃの安全性を確認し、子供たちの交流を見守る。 - 音楽遊びの際に音量や選曲に配慮し、聴覚への負担を考慮する。 - 手作りおもちゃの素材選定に注意し、安全な遊び環境を整える。 です。"
compressed = compress_to_encoded_uri_component(original_string)
print("Compressed:", compressed)

decompressed = decompress_from_encoded_uri_component(compressed)
print("Decompressed:", decompressed)
print("Original and decompressed are equal:", original_string == decompressed)