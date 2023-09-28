import sys
import os
# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

sys.path.append(os.path.dirname(script_dir))

from service.qy_weixin import qy_weixin

qy_weixin.send_message('出现了怪兽 \n<a href=\"http://ec2-18-144-88-173.us-west-1.compute.amazonaws.com/ops/2023-09-11\">点此查看</a> 加油💪！')