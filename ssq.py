import re
import requests
import json 
from bs4 import BeautifulSoup
import os
import easygui


_path = os.path.split(os.path.abspath(__file__))[0]

class Ssq():
    def __init__(self) -> None:
        self.session = requests.session()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'zjflcp.zjol.com.cn',
            'Referer': 'http://zjflcp.zjol.com.cn/fcweb/index.html',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69'}

        # 蓝球数量 * 10 + 红球数量 为 key，value 对应奖级
        self.prize_level = {
            0: 6,
            1: 6,
            2: 6,
            3: 6,

            10: 5,
            11: 5,
            12: 5,

            13: 4,
            4: 4,

            14: 3,
            5: 3,

            15: 2,

            6: 1,

            16: 0
        }

        fn = os.path.join(_path,'my_lottery.json')
        with open(fn,'r',encoding='utf8') as f:
            self.my_lottery = json.load(f)
        
    def fetch_data(self):
        # 从浙江福彩双色球首页进入
        url = 'http://zjflcp.zjol.com.cn/fcweb/ssq.html'
        r = self.session.get(url,headers=self.headers)
        s = r.text

        # 找到最新期数
        s = re.search('qishu=\d+',s).group()
        qishu = re.search('\d+',s).group()
        self.last_no = qishu 

        # 进入最新期数的开奖页面
        url = 'http://zjflcp.zjol.com.cn/fcweb/ssq_d.html?qishu={:s}'.format(qishu)
        r = self.session.get(url,headers = self.headers)
        s = r.text 
        # with open('txt.txt','w',encoding= 'utf8') as f:
        #     f.write(s)

        # 获取开奖结果和各级奖金 
        result = self.get_result(s)
        self.balls = result[:2]
        self.rewards = result[2]
        self.rewards.append(0)


    def check_result(self):

        reds = self.balls[0]
        blue = self.balls[1]

        
        # print('开奖日期: {}'.format(self.last_dt))
        result = '开奖日期: {}\n'.format(self.last_dt) 
        # print('开奖期数: {}\n'.format(self.last_no))
        result +=  '开奖期数: {}'.format(self.last_no)
        # print('开奖号码:{}'.format(self.balls))
        result += '开奖号码:{}\n'.format(self.balls)

        for group in self.my_lottery:
            # print('{}:'.format(group))
            result += '{}:\n'.format(group)
            for my_lottery in self.my_lottery[group]:

                balls = my_lottery.split('+')
                my_reds = balls[0].split(',')
                my_blue = balls[1]

                r = 0
                matched_red = []
                matched_blue = ''

                for red in my_reds:
                    if red in reds:
                        r += 1
                        matched_red.append(red)
                
 

                if my_blue == blue:
                    r += 10
                    matched_blue = blue
 
                reward_level = self.prize_level[r]
                reward = self.rewards[reward_level]
                # print('{}, red {:<16s}, blue{:>2s}，奖金：{}'.format(my_lottery,str(matched_red),matched_blue,reward))
                result += '{}, red {:<16s}, blue{:>2s}，奖金：{}\n'.format(my_lottery,str(matched_red),matched_blue,reward)
        return result


    def get_result(self,s):


        soup = BeautifulSoup(s,features="lxml")

        reds = []
        balls = soup.find_all(name = 'ul',attrs= {'class':'ssqUl'})

        dt_ = str(soup.find_all(attrs = {'class':'ssqTopRig'})[0])
        dt = re.search('\d+.*<',dt_).group()[:-10]
        self.last_dt = dt 
        s_balls = str(balls)
        l_balls = re.findall('\d+',s_balls)
        reds =l_balls[:6]
        blue = l_balls[-1]

        amounts = soup.find_all(name = 'li',attrs= {'class':'amount'})

        s_amounts = str(amounts)
        amounts = re.findall('\d+',s_amounts)

        return [reds,blue,amounts]





if __name__ == '__main__':

    ssq = Ssq()
    ssq.fetch_data()
    r = ssq.check_result()
    easygui.msgbox(r)    
