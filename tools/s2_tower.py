# -*- coding: utf-8 -*-
"""2장 — 별빛 관측탑, 서리별"""


def build(S):
    S.line(bg="observatory", bgm="night", ch="2장 · 매일 아침", hide=True, hide2=True,
           text="그날부터 매일 아침 관측탑에 올랐다. 해 뜨기 전, 별이 아직 남아 있을 때.")
    S.line(text="엘리제는 항상 먼저 와 있었다. 몇 시에 오는지 물어봤더니, 대답 대신 눈썹을 올렸다.")
    S.line(show={"id": "elize", "expr": "base"}, who="엘리제", e="base",
           text="오늘은 마력의 길을 세 개만 걸어. 네 몸이 기억하는 속도가 있어. 그걸 넘기면 다 잊어.")
    S.line(who="나", text="선배님은 몇 개 걷는데요?")
    S.line(who="엘리제", e="base", text="이십사 개. 한 번에.")
    S.line(who="나", text="…그건 자랑입니까?")
    S.line(who="엘리제", e="base", text="경고야. 너는 나처럼 되면 안 돼. 나는 십 년 걸렸어.")
    S.line(text="그 말에는 숫자가 있어서, 숫자가 무서웠다.")
    S.line(text="사흘째에 마법진 하나가 손 끝에서 완전히 밝아졌다. 닷새째에는 두 개가 동시에.")
    S.line(text="엘리제는 칭찬하지 않았다. 대신 다음 날 아침, 내 자리에 수첩을 하나 놓고 갔다. 표지에 아무것도 안 적힌 수첩.")
    S.line(text="안에는 열두 주 분량의 계획이 적혀 있었다. 하루도 빠짐없이.")

    S.line(bg="observatory", bgm="tense", ch="2장 · 열두 번째 아침", hide=True, hide2=True,
           text="열두 번째 아침에 일이 생겼다.")
    S.line(text="평소보다 한 걸음 더 걸었다. 욕심이었다. 마법진이 밝아지다가, 급하게 어두워졌다.")
    S.line(text="마력이 돌아 나왔다. 손끝이 뜨겁고, 그다음이 없다는 느낌. 숨이 안 쉬어졌다.")
    S.line(show={"id": "elize", "expr": "serious"}, who="엘리제", e="serious", text="편입생!")
    S.line(text="그녀가 내 손을 잡았다. 평소보다 세게. 그리고 마력이 그녀 쪽으로 빠져나갔다.")
    S.line(text="시야가 돌아왔다. 숨이 들어왔다. 무릎이 풀려서 앉았다.")
    S.line(show={"id": "elize", "expr": "surprised"}, who="엘리제", e="surprised", text="…아.")
    S.line(text="그녀가 손을 놓았다. 손등이 빨갰다. 화상이었다. 마력이 그녀를 태운 거였다.")
    S.line(who="나", text="선배님, 손이.")
    S.line(who="엘리제", e="base", text="괜찮아. 원래 이래. 금방 나아.")
    S.line(text="그녀가 손을 로브 소매 안으로 넣었다. 아주 익숙한 동작이었다. 처음 하는 동작이 아니었다.")
    S.line(text="그때 알았다. 지난 십이 일 동안, 매일 아침, 내가 마력을 다루는 동안 그녀가 그 자리에 서 있었다는 뜻을.")

    S.choice([
        {"t": "\"다음부터는 제가 잡겠습니다.\"", "to": "d2_hand_mine", "eff": {"elize": 3}, "flag": "tower_hand"},
        {"t": "\"왜 아픈 걸 알면서 잡으세요.\"", "to": "d2_ask_why", "eff": {"elize": 2}},
        {"t": "화상 얘기는 하지 않고, 수첩만 챙긴다.", "to": "d2_silent"},
    ])

    S.label("d2_hand_mine")
    S.line(who="나", text="다음부터는 제가 잡겠습니다. 제가 선배님 손을.")
    S.line(who="엘리제", e="surprised", text="…뭐?"
    )
    S.line(who="나", text="제 마력이 선배님을 태우잖아요. 그럼 순서를 바꾸면 되죠. 제가 먼저 잡으면, 제 쪽에서 막을 수 있어요.")
    S.line(hide=False, show={"id": "elize", "expr": "base"}, who="엘리제", e="base",
           text="그게 그렇게 되는 게 아니야. 마력은 네 몸에서 나오니까, 네가 먼저 잡아도 결국 내가 아파.")
    S.line(who="나", text="그럼 반씩 하죠. 번갈아서.")
    S.line(text="그녀가 잠깐 나를 봤다. 이번에는 계산하는 얼굴이 아니라, 다른 얼굴이었다.")
    S.line(who="엘리제", e="blush", text="…너, 생각보다 고집이 세네.")
    S.line(who="나", text="선배님한테 배웠습니다.")
    S.line(who="엘리제", e="blush", text="나는 고집이 아니야. 정확한 거야.")
    S.line(text="그렇게 말하면서 그녀는 손을 조금 웃도 안쪽으로 넣었다. 화상을 숨기려고.")
    S.line(text="나는 그날 오후, 도린에게 치유과 사람을 소개해 달라고 했다. 소개받을 필요도 없었다. 온실은 처음부터 알고 있었다.")
    S.goto("d2_merge_hand")

    S.label("d2_ask_why")
    S.line(who="나", text="왜 아픈 걸 알면서 잡으세요.")
    S.line(who="엘리제", e="base", text="안 잡으면 네가 더 아플걸.")
    S.line(who="나", text="그건 제가 아픈 거고, 이건 선배님이 아픈 거잖아요.")
    S.line(who="엘리제", e="serious", text="…그걸 왜 그렇게 따져.")
    S.line(who="나", text="따지는 게 아니라, 이해를 못 하겠어서요.")
    S.line(text="그녀가 소매를 여몄다. 손등에 화상이 세 군데 있었다. 하나는 오늘 생긴 것이고, 둘은 조금 오래된 것.")
    S.line(who="엘리제", e="base", text="나한테 아픈 건 습관이야. 열 살 때부터 했으니까. 네가 아픈 건 사고고.")
    S.line(who="엘리제", e="base", text="습관을 고치는 것보다 사고를 막는 게 쉬워. 그래서 이렇게 해.")
    S.line(text="그 말이 이상하게 오래 남았다. 습관이라는 단어가 사람에게 이렇게 무거울 수 있다는 걸 그때 알았다.")
    S.goto("d2_merge_hand")

    S.label("d2_silent")
    S.line(text="아무 말도 하지 않았다. 대신 수첩을 집어 들고 일어나서, 그녀의 옆자리에 앉았다.")
    S.line(text="평소에는 서로 마주 보고 앉았다. 오늘은 나란히 앉았다.")
    S.line(who="엘리제", e="surprised", text="…왜 옆에 앉아.")
    S.line(who="나", text="선배님이 손을 숨길 거면, 제가 그 손 쪽에 앉는 게 맞잖아요.")
    S.line(who="엘리제", e="base", text="…그건 또 무슨 논리야.")
    S.line(text="그녀는 한참 아무 말도 하지 않았다. 수첩은 펴 놓은 채였다. 그날 아침에는 세 개 중 하나밖에 못 걸었다.")
    S.line(who="엘리제", e="base", text="편입생. 너, 이상해.")
    S.line(who="나", text="자주 듣는 말이에요.")
    S.goto("d2_merge_hand")

    S.label("d2_merge_hand")
    S.line(bg="greenhouse", bgm="warm", show={"id": "seia", "expr": "base"}, hide2=True,
           text="그날 오후, 온실. 세이아가 내 손에서 그녀의 손으로 시선을 옮겼다.")
    S.line(who="세이아", e="surprised", text="이거, 오늘 생겼어요? 성좌반 선배 손등이에요?")
    S.line(who="나", text="…네가 알겠어요?")
    S.line(who="세이아", e="base", text="손등만으로도 알아요. 이 사람 마력이 얼마나 센지. 화상 자국이 나이를 먹고 있어요.")
    S.line(text="그녀가 약초를 갈았다. 이번에는 손이 느렸다. 무언가를 생각하면서 가는 손이었다.")
    S.line(who="세이아", e="base", text="후배님. 물어봐도 돼요?")
    S.line(who="나", text="네.")
    S.line(who="세이아", e="serious", text="후배님이 아팠을 때, 그 선배가 손을 잡아 줬죠.")
    S.line(who="나", text="…네.")
    S.line(who="세이아", e="serious", text="그거, 좋은 방법이에요. 나쁘지 않아요. 근데 그건 그 사람이 아파지는 방법이에요.")
    S.line(who="세이아", e="base", text="제가 아는 걸 하나 알려줄까요. 마력은 한 사람 몸에만 있으면 언젠가 터져요. 그래서 옛날 마법사들은 손을 잡았어요.")
    S.line(who="세이아", e="base", text="두 사람이 나눠 가지면, 아무도 안 터져요. 대신 아주 조금씩 아프고요.")
    S.line(who="나", text="…그럼 아무도 안 아프게 하는 건요?")
    S.line(who="세이아", e="base", text="세 명이면, 더 조금씩 아파요.")
    S.line(text="그녀는 웃으면서 그렇게 말했다. 그 말을 나는 이 장면에서 처음 들었지만, 나중에 아주 오래 기억하게 된다.")
    S.line(who="세이아", e="base", text="자, 손. 약 올릴게요. 그리고 이거, 선배한테 전해 주세요. 손등에 바르라고요. 이름은 말하지 말고요.")
    S.line(who="나", text="이름을 왜요?")
    S.line(who="세이아", e="blush", text="성좌반 선배는 아마 저를 모를 거예요. 이름 대면 안 받아요. 그냥 약이라고 하세요.")

    S.line(bg="observatory", bgm="night", ch="2장 · 서리별", hide2=True, hide=True,
           text="저녁, 관측탑. 약을 건네자 엘리제는 한참 뚜껑을 들여다봤다.")
    S.line(show={"id": "elize", "expr": "base"}, who="엘리제", e="base", text="이거, 치유과 약이야. 누가 줬어.")
    S.line(who="나", text="그냥… 아는 사람이요.")
    S.line(who="엘리제", e="base", text="온실지기. 세이아. 이름은 알아. 작년에 온실에서 마력 폭주한 애 살린 사람이래.")
    S.line(who="나", text="…아세요?")
    S.line(who="엘리제", e="base", text="성좌반은 마력을 다루니까, 누가 잘 다루는지도 알아야 해. 그 애는 손이 좋아. 손이 사람을 살리는 쪽으로만 쓰여.")
    S.line(text="그녀가 약을 발랐다. 그리고 망원경 쪽으로 걸어가면서 말했다.")
    S.line(who="엘리제", e="base", text="이리 와. 오늘은 별을 볼 거야.")
    S.line(text="망원경을 들여다봤다. 별 하나가 아주 작게 떨고 있었다. 다른 별들은 가만히 있는데 그것만.")
    S.line(who="엘리제", e="base", text="서리별. 오래된 별이야. 혼자서는 못 빛나. 옆의 별한테 빛을 받아서 빛나.")
    S.line(who="엘리제", e="base", text="어릴 때 내가 이 별에 내 이름을 붙였어. 선생님이 웃었지. 별에 이름을 붙이는 건 신의 일이라고.")
    S.line(who="나", text="선배님 별이네요.")
    S.line(who="엘리제", e="blush", text="…어릴 때 얘기야.")
    S.line(text="그녀가 망원경에서 물러나고, 내가 그 자리에 섰다. 어깨가 거의 닿을 거리였다.")
    S.line(who="엘리제", e="base", text="편입생. 하나만 물을게. 너는 마법을 왜 배우고 싶어.")
    S.line(text="대답을 바로 못 했다. 마석이 갈라진 날부터 지금까지, 그걸 생각할 시간이 없었다.")
    S.choice([
        {"t": "\"제 몸이 남을 다치게 하지 않게 되고 싶어서요.\"", "to": "d2_why_protect", "eff": {"elize": 2}, "flag": "wish_protect"},
        {"t": "\"제가 뭔지 알고 싶어서요.\"", "to": "d2_why_know", "eff": {"elize": 1}, "flag": "wish_know"},
        {"t": "\"선배님처럼 되고 싶어서요.\"", "to": "d2_why_like", "eff": {"elize": 1}},
    ])

    S.label("d2_why_protect")
    S.line(who="나", text="제 몸이 남을 다치게 하지 않게 되고 싶어요. 그게 마법을 배우는 이유가 될 수 있는지 모르겠지만.")
    S.line(text="그녀가 아주 오래 나를 봤다. 별빛이 눈에 걸려 있었다.")
    S.line(who="엘리제", e="base", text="…그거, 내가 열 살 때 했던 생각이야.")
    S.line(who="엘리제", e="base", text="나쁘지 않아. 나쁘지 않은데, 그걸로 십 년을 버티면 좀 힘들어. 나처럼.")
    S.line(who="나", text="선배님은 버티셨잖아요.")
    S.line(who="엘리제", e="base", text="버틴 게 아니라, 버텨진 거야. 차이가 있어.")
    S.line(text="그 말을 하면서 그녀는 아주 짧게 웃었다. 처음 본 웃음이었다. 예쁘다기보다, 오래된 웃음이었다.")
    S.goto("d2_end")

    S.label("d2_why_know")
    S.line(who="나", text="제가 뭔지 알고 싶어서요. 마석이 갈라지고, 마법진이 켜지고, 남의 손을 태우는 게 저인지 아닌지.")
    S.line(who="엘리제", e="base", text="그건 좋은 이유야. 적어도 거짓말은 아니야.")
    S.line(who="엘리제", e="base", text="근데 조심해. 자기를 알아가는 데만 십 년 쓰면, 정작 자기 인생은 안 남아.")
    S.line(who="나", text="선배님은요?")
    S.line(who="엘리제", e="base", text="…나는 그 십 년을 썼어. 그래서 지금 이렇게 서 있어.")
    S.line(text="농담처럼 말했는데, 농담이 아니었다. 그걸 지적하지 않기로 했다.")
    S.goto("d2_end")

    S.label("d2_why_like")
    S.line(who="나", text="선배님처럼 되고 싶어서요.")
    S.line(who="엘리제", e="surprised", text="…나?")
    S.line(who="나", text="아무도 안 다치게 하면서, 마법진 하나로 스물네 명을 세우는 사람이잖아요. 그거 멋있어요.")
    S.line(text="그녀가 잠깐 아무 말도 못 했다. 그리고 아주 낮게 말했다.")
    S.line(who="엘리제", e="blush", text="…그렇게 말하는 사람, 너밖에 없어.")
    S.line(who="나", text="그럼 제가 맞는 거네요.")
    S.line(who="엘리제", e="blush", text="그런 논리로 자꾸 사람을 이기지 마.")
    S.goto("d2_end")

    S.label("d2_end")
    S.line(text="탑을 내려오는 계단에서, 그녀가 뒤에서 말했다. 나는 계단 아래에 서서 고개를 들었다.")
    S.line(who="엘리제", e="base", text="내일부터는 열여덟 번째 계단에서 기다려. 위에서 부르면 뛰어올라오지 마. 넘어져.")
    S.line(who="나", text="…네.")
    S.line(text="열여덟 번째 계단. 그 숫자를 기억했다. 나중에 이 계단을 오르는 날이 올 줄은 몰랐다.")
    S.line(text="2장이 그렇게 끝났다. 십 주가 남았다.")
