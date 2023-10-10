

Pytorch 관련해서 자동으로 device 찾는 함수.

배포 관련해서 api key 보이지 않도록 수정. (git이나 올릴 때는 .gitignore 해서 올리면 됩니다.)

==> 일단은 api key값 선택에 따라서 바뀌게 만들기+
==> embedding 서버에 없으면 다운로드 체크

만드는게 목표

+ 목표 낼 때 간혹 오류 뜨는데 reParsing하는거 고려(찾아보면 나올듯?)
+ DataChunking 관련해서 큰 틀에서 또 작은걸로 짜르고 다시 찾아오는 형태의 발전된 RAG로 만들어서 해보기