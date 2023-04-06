
import requests, json, os, time, bs4, sys, re
#3导入wordpress_xmlrpc模块
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost

# pid=31  后端开发  &cid=0 全部 type=4 最新 2 热门  page 1  page_size 30  is_index 精选 is_subject 话题 is_rank 1  上榜

img_path = 'img'
base_url = '/img/'

headers = {
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

def get_article_json(page: int = 1):
  if os.path.exists('article.json'):
    with open('article.json', 'r', encoding='utf-8') as f:
      article_json = json.load(f)
      return article_json
  pid = 31
  cid = 0
  _type = 2
  page_size = 30
  is_index = 1
  is_subject = 0
  is_rank = 0
  url = f'https://blog.51cto.com/getNavBlogList?pid={pid}&cid={cid}&type={_type}&page={page}&page_size={page_size}&is_index={is_index}&is_subject={is_subject}&is_rank={is_rank}'
  res = requests.get(url, headers = headers)

  return json.loads(res.text)


has_download = []
try:
  with open('has_download.txt', 'r', encoding='utf-8') as f:
    has_download = json.load(f)
except:
  pass

page = 1
while True:
  article_json = get_article_json(page)

  # pv > 50 and not in has_download

  article_url = None
  article_tag = []
  article_title = ''
  article_id = ''
  for article in article_json['data']['list']:
    if article['pv'] > 500 and article['id'] not in has_download and '第' not in article_title:
      article_url = article['blog_url']
      article_tag = [ x for x in article['tags'].keys() ]
      article_title = article['title']
      article_id = article['id']
      has_download.append(article['id'])
      break
  

  if article_url is not None:
    break
  else:
    page += 1


def get_article_html():
  if os.path.exists('article.html'):
    with open('article.html', 'r', encoding='utf-8') as f:
      article_html = f.read(-1)
      return article_html
  html = requests.get(article_url, headers=headers)
  # with open('article.html', 'w', encoding='utf-8') as f:
  #   f.write(html.text)
  return html.text
print(article_url)
html = get_article_html()

key_word = 'id="container" data-element="root">'
start = html.find(key_word)
if (start <= 0):
  key_word = 'id="markdownContent">'
  start = html.find(key_word)
start += len(key_word)

# key_word = '<h'
# start = html.find(key_word, start)
# if (start < 0):
#   raise ValueError()


key_word_end = '<div id="asideoffset"></div>'
end = html.find(key_word_end, start)

style = '''
<style>
.code-toolbar {
    box-shadow: inset 0 1px 2px hsla(0,0%,100%,.1), inset 40px 0 0 rgb(102 128 153/5%), 0 1px 0 rgb(102 128 153/5%);
    position: relative;
}
.code-toolbar {
    font-size: 14px;
}
.hljs-cto {
    position: relative;
}
.operation_box {
    display: flex;
    display: none;
    position: absolute;
    right: 10px;
    top: 10px;
    z-index: 99;
}
.hljs-cto pre {
    box-sizing: border-box;
    width: 100%!important;
}
:not(pre)>code[class*=language-], pre[class*=language-] {
    background: #f7f7f7;
    -webkit-box-sizing: border-box;
    -moz-box-sizing: border-box;
    box-sizing: border-box;
    margin-bottom: 1em;
}
pre[class*=language-] {
    background: rgba(102,128,153,.05);
    box-shadow: inset 0 1px 2px hsla(0,0%,100%,.1), inset 40px 0 0 rgba(102,128,153,.05), 0 1px 0 rgba(102,128,153,.05);
    display: block;
    margin-bottom: 10px;
    overflow-x: auto;
    padding: 10px 25px 10px 55px!important;
}
code[class*=language-], pre[class*=language-] {
    word-wrap: normal;
    background: 0 0;
    color: #000;
    font-family: Monaco,Menlo,Consolas,Courier New,monospace!important;
    -webkit-hyphens: none;
    -moz-hyphens: none;
    -ms-hyphens: none;
    hyphens: none;
    line-height: 1.6;
    text-align: left;
    white-space: pre;
    word-break: normal;
    word-spacing: normal;
}
pre[class*=language-] {
    overflow: hidden;
    padding: 7px 25px 7px 55px;
}
code[class*=language-], pre[class*=language-] {
    border-radius: 4px;
    color: #333;
    font-family: Monaco,Menlo,Consolas,Courier New,monospace;
    font-size: 1em;
    line-height: 2;
    padding: 0.5em 1em;
    -moz-tab-size: 4;
    -o-tab-size: 4;
    tab-size: 4;
}
pre[class*=language-] {
    box-shadow: unset!important;
}
.editor-preview pre, .editor-preview-side pre {
    background: #f7f7f7;
    margin-bottom: 10px;
}
.main-content .highlight pre, .main-content pre {
    line-height: 1.45;
    overflow: auto;
    padding: 1rem 1.5rem;
}
.main-content pre {
    overflow: auto;
}
code, pre {
    font-size: 14px;
}
pre[class*=language-]>code {
    position: relative;
}

.main-content pre code, .main-content pre tt {
    word-wrap: normal;
    background-color: transparent;
    border: 0;
    line-height: inherit;
    margin: 0;
    max-width: none;
    padding: 0;
}
</style>
'''
content = '<div>' + html[start:end].strip() + '</div>'
content = content.replace("  ", " ")
# content = content.replace("\n", " ")
content = content.replace("转载请注明出处", "谢谢")
content = content.replace("转载注明出处", "谢谢")
content = content.replace("<colgroup>", "<colgroup1>")
content = content.replace("</colgroup>", "</colgroup1>")
with open('content.html', 'w', encoding='utf-8') as f:
  f.write(content)

# 图片处理
def download_img(url):
  url = url.split('?')[0]
  rep = requests.get(url, headers=headers)
  file_name = f'{int(time.time() * 1000)}.jpg'
  if (not os.path.exists(img_path)):
    os.makedirs(img_path)
  with open(f'{img_path}/{file_name}', 'wb+') as f:
    f.write(rep.content)
  return file_name

def filter_tag(soup):
  global content
  tags = ['blockquote', 'p']
  for tag in tags:
    if content.startswith('<div><' + tag):
      _tag = soup.select_one(tag)
      if (len(_tag.prettify()) > 50) or '作者' in _tag.prettify():
        # print(r"^<div><" + tag + r"(.*)</" + tag + r'>')
        idx = content.find(f'</{tag}>')
        content = '<div>' + content[idx + len(f'</{tag}>'):]# re.compile(r"^<div><" + tag + r"(.*?)</" + tag + r'>').sub('<div>', content)
        # print(content)
        # content = content.replace(r"^<div><" + tag + r".*</" + tag + r'>', "<div>")
        filter_tag(bs4.BeautifulSoup(content, 'html.parser'))
      break

soup = bs4.BeautifulSoup(content, 'html.parser')
filter_tag(soup)
imgs = soup.select('img')
replace_src_list = []

for img in imgs:
  if 'src' in img.attrs.keys():
    src = img.attrs['src']
    if len(src) > 0 and src.startswith('http'):
      filename = download_img(src)
      replace_src_list.append((src, base_url + filename))

# print(replace_src_list)
for t in replace_src_list:
  content = content.replace(t[0], t[1])

content = content.replace("  ", " ")
with open('content.html', 'w', encoding='utf-8') as f:
  f.write(content)

img ='<img style="display: none" src="https://blog.miao7.cn/wp-content/themes/kratos-4.1.6/assets/img/default.jpg" />'
if (len(replace_src_list) > 0):
  img =f'<img style="display: none" src="{replace_src_list[0][1]}" />'
post = {
  'title': article_title,
  'url': article_id,
  'category': ['技术分享'],
  'post_tag': article_tag,
  'content': img + '<div style="width:100%;">' + content[len('<div>'):]
}

def send_to_wordpress(post, base_url, username, password):
  wp = Client(base_url + '/xmlrpc.php',username,password)
  #现在就很简单了,通过下面的函数,将刚才获取到数据赋给对应的位置
  send_post = WordPressPost()
  send_post.title = post['title']
  # post.slug文章别名
  #我网站使用%post name%这种固定链接不想一长串,这里是最初md文章URL的参数,英文连字符格式
  if post['url'] is not None:
    send_post.slug = post['url']
  send_post.content = post['content']
  #分类和标签,分类标签不存在会自动创建
  send_post.terms_names = {
    'post_tag': post['post_tag'],
    'category': post['category']
  }
  # post.post_status有publish发布、draft草稿、private隐私状态可选,默认草稿。如果是publish会直接发布
  send_post.post_status = 'draft'
  #推送文章到WordPress网站
  wp.call(NewPost(send_post))

name = sys.argv[1]
password = sys.argv[2]
send_to_wordpress(post, 'https://blog.miao7.cn', name, password)

with open('has_download.txt', 'w', encoding='utf-8') as f:
  json.dump(has_download, f)
