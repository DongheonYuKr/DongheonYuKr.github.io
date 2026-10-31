# DongheonYuKr.github.io
DongheonYuKr.github.io

## 미리 써 둔 글(_draft_) 공개하는 법

`content/`에서 이름이 `_`로 시작하는 파일은 빌드에서 빠집니다(미리 써 둔 글).
올릴 날 아침에 **그날 글 하나만** 이름 앞의 `_draft_`를 떼고 빌드·커밋·푸시합니다.

| 올릴 날 | 파일 |
|---|---|
| 11-02 | `_draft_07_github-agent-reach.html` |
| 11-03 | `_draft_08_github-hyperframes.html` |
| 11-04 | `_draft_09_github-taste-skill.html` |
| 11-05 | `_draft_10_github-voicestudio.html` |

예) 11-02 아침:

    git mv content/_draft_07_github-agent-reach.html content/07_github-agent-reach.html && python3 build.py && git add -A && git commit -m "깃허브 털기 #02 공개" && git push

`/new/`와 `/free/` 아래 「깔아 본 도구」 목록은 빌드할 때 자동으로 새 글을 따라갑니다.
