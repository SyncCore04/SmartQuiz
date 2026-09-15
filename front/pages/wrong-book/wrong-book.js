Page({
  data: {
    wrongList: [
      { id: 1, num: 4, title: '下列文学作品与其作者对应正确的是？', myAnswer: 'A.《红楼梦》-施耐庵', correctAnswer: 'B.《西游记》-吴承恩', analysis: '《红楼梦》的作者是曹雪芹，《西游记》的作者是吴承恩，对应正确的是B选项。' },
      { id: 2, num: 9, title: '唐朝的开国皇帝是谁？', myAnswer: 'A.李世民', correctAnswer: 'B.李渊', analysis: '唐朝的开国皇帝是李渊（唐高祖），李世民是第二任皇帝（唐太宗）。' },
      { id: 3, num: 12, title: '下列哪个不属于三大合成材料？', myAnswer: 'C.陶瓷', correctAnswer: 'D.水泥', analysis: '三大合成材料是塑料、合成纤维、合成橡胶。水泥不属于三大合成材料。' },
      { id: 4, num: 15, title: 'The news _____ very exciting.', myAnswer: 'A.is', correctAnswer: 'B.are', analysis: 'news是不可数名词，谓语动词用单数。但本题考察的是特定语境，正确答案应为is。', correctAnswer2: 'A.is' },
      { id: 5, num: 18, title: '等差数列求和公式Sn=?', myAnswer: 'S=n/2×a', correctAnswer: 'Sn=n(a1+an)/2', analysis: '等差数列前n项和公式为Sn=n(a1+an)/2=na1+n(n-1)d/2。' },
      { id: 6, num: 22, title: '地球自转一周需要多长时间？', myAnswer: '12小时', correctAnswer: '24小时', analysis: '地球自转一周约需要24小时（23小时56分4秒），这是一天的来源。' }
    ]
  },
  onLoad() {}
})
