#!python
# -*- coding:utf-8 -*-

#1导入frontmatter模块
import sys
from frontmatter import Frontmatter
#2.1导入markdown模块
import markdown
#3导入wordpress_xmlrpc模块
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost

def markdown_to_html(md):
  #2.1markdown库导入
  post_content_html = markdown.markdown(md, extensions=['markdown.extensions.fenced_code'])
  post_content_html = post_content_html.encode("utf-8")
  return post_content_html

def load_markdown_info(dir_md):
  #通过front matter.load函数加载读取文档里的信息
  #这里关于Python-front matter模块的各种函数使用方式GitHub都有说明,下面直接贴可实现的代码
  post = Frontmatter.read_file(dir_md)
  #将获取到的信息赋值给变量
  post_title=post['attributes']['title']
  post_tag = post['attributes']['tag']
  post_category = post['attributes']['category']
  post_url = post['attributes']['url']
  return {
    'title': post_title,
    'url': post_url,
    'content': markdown_to_html(post['body']),
    'post_tag': post_tag,
    'category': post_category
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



if __name__ == '__main__':
  dir_md = sys.argv[1]
  send_to_wordpress(load_markdown_info(dir_md), 'https://blog.miao7.cn', 'xxx', 'xxxxxxx')







