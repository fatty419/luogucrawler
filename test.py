import unittest

import requests

from main import get_question

class TestGetQuestion(unittest.TestCase):
    def test_get_question(self):
        cookie = {
            '_uid': '1097055',
            '__client_id': '6d44000048a6adae6f6f7b4405948d69419b9c06',
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}
        Problemurl = "https://www.luogu.com.cn/problem/P1000"
        resp = requests.get(Problemurl, headers=headers, cookies=cookie)
        # P1000页面的HTML代码
        html = resp.text
        # 预期的题目Markdown内容
        expected_md = """
# 超级玛丽游戏
## 题目背景
本题是洛谷的试机题目，可以帮助了解洛谷的使用。

建议完成本题目后继续尝试 [P1001](/problem/P1001)、[P1008](/problem/P1008)。  

另外强烈推荐[新用户必读贴](/discuss/show/241461)

## 题目描述
超级玛丽是一个非常经典的游戏。请你用字符画的形式输出超级玛丽中的一个场景。

```
                ********
               ************
               ####....#.
             #..###.....##....
             ###.......######              ###            ###
                ...........               #...#          #...#
               ##*#######                 #.#.#          #.#.#
            ####*******######             #.#.#          #.#.#
           ...#***.****.*###....          #...#          #...#
           ....**********##.....           ###            ###
           ....****    *****....
             ####        ####
           ######        ######
##############################################################
#...#......#.##...#......#.##...#......#.##------------------#
###########################################------------------#
#..#....#....##..#....#....##..#....#....#####################
##########################################    #----------#
#.....#......##.....#......##.....#......#    #----------#
##########################################    #----------#
#.#..#....#..##.#..#....#..##.#..#....#..#    #----------#
##########################################    ############
```
## 输入输出格式
#### 输入格式

无
#### 输出格式

如描述
## 输入输出样例
暂无测试点
## 说明
**广告**

洛谷出品的算法教材，帮助您更简单的学习基础算法。[【官方网店绝赞热卖中！】&gt;&gt;&gt;](https://item.taobao.com/item.htm?id=637730514783)

[![](https://cdn.luogu.com.cn/upload/image_hosting/njc7dlng.png)](https://item.taobao.com/item.htm?id=637730514783)
"""
        expected_ques = "超级玛丽游戏"  # 预期的题目标题
        md, ques = get_question(html)
        self.assertEqual(md, expected_md)  # 验证返回的Markdown内容是否与预期一致
        self.assertEqual(ques, expected_ques)  # 验证返回的题目标题是否与预期一致
if __name__ == '__main__':
    unittest.main()


