//+——————————————————————+
//|                                                       Zigzag.mq4 |
//|                 Copyright ?2005-2007, MetaQuotes Software Corp. |
//|                                       http://www.metaquotes.net/ |
//+——————————————————————+
#property copyright “Copyright ? 2007, MetaQuotes Software Corp.”
#property link      “http: // www.metaquotes.net/”

// Mt4特有的指标属性设置
#property indicator_chart_window // 主窗口进行指标显示
#property indicator_buffers 1    // 指标运用到数值的个数
#property indicator_color1 Red   // 指标显示颜色
// —- indicator parameters
// Zigzag的三个参数
extern int ExtDepth = 12;
extern int ExtDeviation = 5;
extern int ExtBackstep = 3;

// —- indicator buffers
// 指标的数值存储变量
double ZigzagBuffer[];  // 拐点
double HighMapBuffer[]; // 高点的临时变量数组
double LowMapBuffer[];  // 低点的临时变量数组

int level = 3;                // recounting’s depth  //最近已知的三个拐点
bool downloadhistory = false; // 是否第一次计算
//+——————————————————————+
//| Custom indicator initialization function                         |
//+——————————————————————+

// Init函数是Mt4指标第一次载入之后运行的初期化函数
int init()
{
  IndicatorBuffers(3); // 对于缓冲储存器分配记忆应用自定义指标计算，用F1可以看到该函数的帮助和解释
  // —- drawing settings
  SetIndexStyle(0, DRAW_SECTION); // 划线的风格
  // —- indicator buffers mapping
  SetIndexBuffer(0, ZigzagBuffer);
  SetIndexBuffer(1, HighMapBuffer);
  SetIndexBuffer(2, LowMapBuffer);
  SetIndexEmptyValue(0, 0.0);

  // —- indicator short name
  IndicatorShortName(”ZigZag(”+ ExtDepth +”,”+ ExtDeviation +”,”+ ExtBackstep +”)”); // 设置指标的简称。
  // —- initialization done
  return (0);
}
//+——————————————————————+
//|                                                                  |
//+——————————————————————+

// start函数是Mt4的主函数，当每次价格变动之后都会触发该函数的执行
int start()
{
  // 变量定义

  // i：临时变量；
  // counted_bars ：用于标识已经计算过的Bar数
  int i, counted_bars = IndicatorCounted();

  // limit：算法中所谓的开始计算位置;
  // counterZ：临时变量
  // whatlookfor：用于标识当前计算的是高点或者低点
  int limit, counterZ, whatlookfor;

  // 以下都是临时变量，具体设值时解释
  int shift, back, lasthighpos, lastlowpos;
  double val, res;
  double curlow, curhigh, lasthigh, lastlow;

  if (counted_bars == 0 && downloadhistory) // history was downloaded
  {                                         // 指标载入时counted_bars为0，而downloadhistory为false，将在下一次价格变化时进行
    ArrayInitialize(ZigzagBuffer, 0.0);
    ArrayInitialize(HighMapBuffer, 0.0);
    ArrayInitialize(LowMapBuffer, 0.0);
  }
  if (counted_bars == 0)
  { // 初期化，第一次运行时limit为除去ExtDepth个图形最初的部分。（算法1.1）
    limit = Bars - ExtDepth;
    downloadhistory = true;
  }
  if (counted_bars > 0)
  { // 如果之前已经计算过，找到最近已知的三个拐点（高点或低点），将计算位置设置为倒数第三个拐点。（算法1.2）
    while (counterZ < level && i < 100)
    {
      res = ZigzagBuffer[i];
      if (res != 0)
        counterZ++;
      i++;
    }
    i--;       // 在上面while中最后一次找到的时候进行+1，所以要-1才能得到真正第三个拐点处。
    limit = i; // 计算位置赋值
    if (LowMapBuffer[i] != 0)
    { // 如果倒数第三个拐点是低点
      curlow = LowMapBuffer[i];
      // 目标在于寻找高点
      whatlookfor = 1;
    }
    else
    {
      curhigh = HighMapBuffer[i];
      whatlookfor = -1;
    }
    for (i = limit - 1; i >= 0; i--)
    { // 清空第三个拐点后的数值，准备重新计算最后的拐点
      ZigzagBuffer[i] = 0.0;
      LowMapBuffer[i] = 0.0;
      HighMapBuffer[i] = 0.0;
    }
  }

  // 算法Step2部分：计算高低点
  for (shift = limit; shift >= 0; shift--)
  {
    // 2.1计算ExtDepth区间内的低点
    val = Low[iLowest(NULL, 0, MODE_LOW, ExtDepth, shift)];
    if (val == lastlow)
      val = 0.0;
    else
    { // 如果该低点是当前低点，
      lastlow = val;
      if ((Low[shift] - val) > (ExtDeviation * Point))
        val = 0.0; // 是否比上个低点还低ExtDeviation，不是的话则不进行回归处理
      else
      { // 找到一个新的低点
        for (back = 1; back <= ExtBackstep; back++)
        { // 回退ExtBackstep个Bar，把比当前低点高点纪录值给清空
          res = LowMapBuffer[shift + back];
          if ((res != 0) && (res > val))
            LowMapBuffer[shift + back] = 0.0;
        }
      }
    }
    // 将新的低点进行记录
    if (Low[shift] == val)
      LowMapBuffer[shift] = val;
    else
      LowMapBuffer[shift] = 0.0;

    // — high
    val = High[iHighest(NULL, 0, MODE_HIGH, ExtDepth, shift)];
    if (val == lasthigh)
      val = 0.0;
    else
    {
      lasthigh = val;
      if ((val - High[shift]) > (ExtDeviation * Point))
        val = 0.0;
      else
      {
        for (back = 1; back <= ExtBackstep; back++)
        {
          res = HighMapBuffer[shift + back];
          if ((res != 0) && (res < val))
            HighMapBuffer[shift + back] = 0.0;
        }
      }
    }
    if (High[shift] == val)
      HighMapBuffer[shift] = val;
    else
      HighMapBuffer[shift] = 0.0;
  }

  // final cutting
  if (whatlookfor == 0)
  {
    lastlow = 0;
    lasthigh = 0;
  }
  else
  {
    lastlow = curlow;
    lasthigh = curhigh;
  }

  // 算法step3.定义指标的高低点
  for (shift = limit; shift >= 0; shift--)
  {
    res = 0.0;
    switch (whatlookfor)
    {
    // 初期化的情况下，尝试找第一个高点或者是地点
    case 0: // look for peak or lawn
      if (lastlow == 0 && lasthigh == 0)
      { // lastlow，lasthigh之前已经初始化，再次判断以保证正确性？
        if (HighMapBuffer[shift] != 0)
        { // 发现高点
          lasthigh = High[shift];
          lasthighpos = shift;
          whatlookfor = -1; // 下个寻找目标是低点
          ZigzagBuffer[shift] = lasthigh;
          res = 1;
        }
        if (LowMapBuffer[shift] != 0)
        { // 发现低点
          lastlow = Low[shift];
          lastlowpos = shift;
          whatlookfor = 1; // 下个寻找目标是高点
          ZigzagBuffer[shift] = lastlow;
          res = 1;
        }
      }
      break;
    case 1: // look for peak      //寻找高点
      if (LowMapBuffer[shift] != 0.0 && LowMapBuffer[shift] < lastlow && HighMapBuffer[shift] == 0.0)
      { // 如果在上个低点和下个高点间发现新的低点，则把上个低点抹去，将新发现的低点作为最后一个低点
        ZigzagBuffer[lastlowpos] = 0.0;
        lastlowpos = shift;
        lastlow = LowMapBuffer[shift];
        ZigzagBuffer[shift] = lastlow;
        res = 1;
      }
      if (HighMapBuffer[shift] != 0.0 && LowMapBuffer[shift] == 0.0)
      { // 发现目标高点
        lasthigh = HighMapBuffer[shift];
        lasthighpos = shift;
        ZigzagBuffer[shift] = lasthigh;
        whatlookfor = -1; // 下一个目标将是寻找低点
        res = 1;
      }
      break;
    case -1: // look for lawn          //寻找低点
      if (HighMapBuffer[shift] != 0.0 && HighMapBuffer[shift] > lasthigh && LowMapBuffer[shift] == 0.0)
      {
        ZigzagBuffer[lasthighpos] = 0.0;
        lasthighpos = shift;
        lasthigh = HighMapBuffer[shift];
        ZigzagBuffer[shift] = lasthigh;
      }
      if (LowMapBuffer[shift] != 0.0 && HighMapBuffer[shift] == 0.0)
      {
        lastlow = LowMapBuffer[shift];
        lastlowpos = shift;
        ZigzagBuffer[shift] = lastlow;
        whatlookfor = 1;
      }
      break;
    default:
      return;
    }
  }

  return (0);
}
//+——————————————————————+