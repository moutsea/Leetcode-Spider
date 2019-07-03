# -*- coding: UTF-8 -*-
import json
from requests_toolbelt.multipart import MultipartEncoder
import bs4
import requests, os
import html2text
import generate

user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'

# 防止一个agent被反爬，所以添加多个
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]


# 将难度转化成markdown当中的标记颜色的语句
def difficulty_transform(st):
    if st == 'Hard':
        return '<font color=red>Hard</font>'
    elif st == 'Medium':
        return '<font color=orange>Medium</font>'
    else:
        return '<font color=green>Easy</font>'


class MySpider(object):

    def __init__(self, path):
        self.base_url = "https://leetcode.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) '
                          ' AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }
        self.num = 1
        self.session = requests.Session()
        self.path = path

    # 模拟登陆
    def login(self, username, password):
        url = 'https://leetcode.com'
        cookies = self.session.get(url).cookies
        for cookie in cookies:
            if cookie.name == 'csrftoken':
                csrftoken = cookie.value

        url = "https://leetcode.com/accounts/login"

        params_data = {
            'csrfmiddlewaretoken': csrftoken,
            'login': username,
            'password': password,
            'next': 'problems'
        }
        headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
                   'Referer': 'https://leetcode.com/accounts/login/', "origin": "https://leetcode.com"}
        m = MultipartEncoder(params_data)

        headers['Content-Type'] = m.content_type
        self.session.post(url, headers=headers, data=m, timeout=10, allow_redirects=False)
        is_login = self.session.cookies.get('LEETCODE_SESSION') != None
        return is_login

    # 获取所有题目的信息
    def get_urls(self):
        html = requests.get('https://leetcode.com/api/problems/all').content
        soup = bs4.BeautifulSoup(html, "html.parser")
        problemstr = soup.prettify()
        problem_map = json.loads(problemstr)
        problemset = problem_map['stat_status_pairs']
        for st in problemset:
            status = st['stat']
            # 跳过付费题
            if st['paid_only']:
                continue
            self.get_problem_by_slug(status['question__title_slug'])

    # 题目的具体信息无法通过直接请求拿到，需要通过graphql传入对应的参数
    # slug是题目名称拼接成的标识
    def get_problem_by_slug(self, slug):
        url = "https://leetcode.com/graphql"
        params = {'operationName': "getQuestionDetail",
                  'variables': {'titleSlug': slug},
                  'query': '''query getQuestionDetail($titleSlug: String!) {
                question(titleSlug: $titleSlug) {
                    questionId
                    questionFrontendId
                    questionTitle
                    questionTitleSlug
                    content
                    difficulty
                    stats
                    similarQuestions
                    categoryTitle
                    topicTags {
                            name
                            slug
                    }
                }
            }'''
                  }
        json_data = json.dumps(params).encode('utf8')
        headers = {'User-Agent': user_agent, 'Connection':
            'keep-alive', 'Content-Type': 'application/json',
                   'Referer': 'https://leetcode.com/problems/' + slug}
        resp = self.session.post(url, data=json_data, headers=headers, timeout=10)
        content = resp.json()
        # 题目详细信息
        question = content['data']['question']
        # print(question)
        self.generate_question_markdown(question)

    # 生成markdown文件
    def generate_question_markdown(self, question):
        text_path = os.path.join(self.path, "{:0>3d}-{}".format(int(question['questionFrontendId']), question['questionTitleSlug']))
        if not os.path.isdir(text_path):
            os.mkdir(text_path)
        with open(os.path.join(text_path, "README.md"), 'w', encoding='utf-8') as f:
            f.write("# （难度{}） Problem {}. {}".format(question['difficulty'], question['questionFrontendId'], question['questionTitle']))
            f.write("\n![{}]({})".format(question['questionTitle'], generate.generate_image(question['questionTitleSlug'], question['questionTitle'])))
            f.write("\n## Link\n[{}](https://leetcode.com/problems/{})\n".format(question['questionTitle'], question['questionTitleSlug']))
            f.write("\n## Difficulty\n\n {}\n".format(difficulty_transform(question['difficulty'])))
            f.write("\n## Description\n\n")
            text = question['content']
            content = html2text.html2text(text).replace("**Input:**", "Input:").replace("**Output:**",
                                                                                        "Output:").replace(
                '**Explanation:**', '## Explanation:').replace('\n    ', '    ')
            f.write(content)

    def run(self):
        self.get_urls()


if __name__ == "__main__":
    mySpider = MySpider('/Users/charles.yin/Documents/leetcode/')
    mySpider.run()