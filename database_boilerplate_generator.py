PLACES = [
    ("近所の公園", "Neighborhood park", "the neighborhood park"),
    ("きらめき中央公園", "Kirameki Central Park", "Kirameki Central Park"),
    ("ショッピング街", "Shopping district", "the shopping district"),
    ("水族館", "Aquarium", "the aquarium"),
    ("動物園", "Zoo", "the zoo"),
    ("植物園", "Botanical garden", "the botanical garden"),
    ("プラネタリウム", "Planetarium", "the planetarium"),
    ("美術館", "Museum", "the museum"),
    ("図書館", "Library", "the library"),
    ("ゲームセンター", "Arcade", "the arcade"),
    ("ボーリング場", "Bowling alley", "the bowling alley"),
    ("カラオケ屋", "Karaoke bar", "the karaoke bar"),
    ("遊園地", "Amusement park", "the amusement park"),
    ("スタジアム", "Stadium", "the stadium"),
    ("映画館", "Movie theater", "the movie theater"),
    ("コンサート会場", "Concert hall", "the concert hall"),
    ("プール", "Swimming pool", "the swimming pool"),
    ("スケート場", "Skating rink", "the skating rink"),
    ("海", "Beach", "the beach"),
    ("スキー場", "Ski resort", "the ski resort"),
    ("神社", "Shrine", "the shrine"),
]

GIRLS = [
    ("伊集院", "Ijuin"),
    ("早乙女", "Saotome"),
    ("藤崎", "Fujisaki"),
    ("如月", "Kisaragi"),
    ("紐緒", "Himoo"),
    ("片桐", "Katagiri"),
    ("古式", "Koshiki"),
    ("清川", "Kiyokawa"),
    ("鏡", "Kagami"),
    ("朝日奈", "Asahina"),
    ("美樹原", "Mikihara"),
    ("虹野", "Nijino"),
    ("優美", "Yumi"),
    ("館林", "Tatebayashi")
]

if __name__ == "__main__":
    output = []

    for girl_jp, girl_en in GIRLS:
        output.append(f"<PNAME>;（今日は、{girl_jp}さんとデートだ）;(I have a date with {girl_en}-san today.)")
        output.append(f"<PNAME>;（今日は、{girl_jp}さんとデートだ）;(Today, I have a date with {girl_en}-san.)")
        output.append(f"<PNAME>;『{girl_jp}さんのことについて知りたいんだけど。;\"\"\"I would like to know about {girl_en}-san.\"\"\"")
        output.append(f"<PNAME>;『よし、次は、{girl_jp}とだ。;(Okay, next time, with {girl_en}-san.)")
        output.append(f"<PNAME>;『しばらく{girl_jp}さんと話し込んだ;(I talked with {girl_en}-san for a while.)")
        output.append(f"<PNAME>;『{girl_jp}さんもいたのか。;\"\"\"Is {girl_en}-san here too?\"\"\"")
        output.append(f"<PNAME>;『あつ、今日は、{girl_jp}さんの誕生日じゃないか。;\"\"\"Ah, today is {girl_en}-san's birthday, isn't it?\"\"\"")
        output.append(f"<PNAME>;（もしかして、{girl_jp}さんを知らず知らずのうちに傷つけてたのかな⋯。）;(Maybe I've unknowingly hurt {girl_en}-san...)")
        output.append(f"<PNAME>;『今日の自由行動は、この前の約束通り{girl_jp}さんと―緒だ。;\"\"\"I'll spend today's free time with {girl_en}-san, as promised.\"\"\"")
        output.append(f"<PNAME>;『まだ{girl_jp}さんは、来ていないようだな。;\"\"\"I see {girl_en}-san has not arrived yet.\"\"\"")
        output.append(f"<PNAME>;（{girl_jp}さんにプレゼントをもらえるなんて、おれは幸せ者だー！）;(I'm so lucky to get a present from {girl_en}-san!)")
        output.append(f"<PNAME>;（神様、何とぞ{girl_jp}さんと今以上に仲良くなれますように。）;(God, please help me get to know {girl_en}-san even better than I already do.)")
        output.append(f"<PNAME>;（おつ、丁度いいところに{girl_jp}さんが来たぞ。）;(Oh, {girl_en}-san arrived just in time.")
        output.append(f"<PNAME>;（あつ、{girl_jp}さん。）;(Oh, {girl_en}-san.)")
        output.append(f"<PNAME>;『よし、次は、{girl_jp}さんとだ;Alright, next is with {girl_en}-san.")
        output.append(f"<PNAME>;『よし、次は、{girl_jp}さんとだ。;Alright, next is with {girl_en}-san.")
        output.append(f"<PNAME>;（{girl_jp}さんを、傷つけたといううわさが、流れてたそうだ。）;There are rumors that I hurt {girl_en}-san.")
        output.append(f"<PNAME>;『{girl_jp}さんのことについて知りたいん;I want to know about {girl_en}.")
        output.append(f"<PNAME>;（どうやら好雄の話では、俺が{girl_jp}さんを、傷つけたといううわさが、流れてたそうだ。）;(According to Yoshio, there's a rumor that I hurt {girl_en}.)")

        for place_jp, place_en, place_en_articled in PLACES:
            output.append(f"<PNAME>;（それじゃ、{place_jp}で、{girl_jp}さんを待つか。）;(Then, let's go to the {place_en_articled} and wait for {girl_en}.)")
            output.append(f"<PNAME>;（それじゃ、{place_jp}で、{girl_jp}さんを待つか。）;(I'll wait for {girl_en} at {place_en_articled} then.)")

    for place_jp, place_en, place_en_articled in PLACES:
        output.append(f"<PNAME>;『 <DATE> に、{place_jp}へ行かない？;\"\"\"Would you like to go to {place_en_articled} on <DATE>?\"\"\"")
        output.append(f"<PNAME>;『{place_jp}の前で待ち合わせでいい？;\"\"\"Can we meet in front of {place_en_articled}?\"\"\"")
        output.append(f"<PNAME>;『それじゃ、 <DATE> に、{place_jp}の前で待ち合わせということで。;\"\"\"So, I'll meet you in front of {place_en_articled} on <DATE>.\"\"\"")

    sorted_output = sorted(output, reverse=True)

    print('\n'.join(output))

