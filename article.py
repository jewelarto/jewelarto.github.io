import re
import codecs
import shutil
import openai
import sys, os
import urllib.request
from PIL import Image
from datetime import date
openai.api_key = "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"
for x in range(0, 10):
  with open("topics.txt", "r") as f:
      topic = f.readline().strip('\n')
      rest = f.read()
  with open("topics.txt", "w") as f:
      f.write(rest)
  response1 = openai.Completion.create(
      model="text-davinci-003",
      prompt=f'Write a short clickbait title for an article about {topic}',
      temperature=0.8,
      max_tokens=200,
      top_p=1.0,
      frequency_penalty=0.5,
      presence_penalty=0.0
    )
  article_title = response1.choices[0].text
  response2 = openai.Completion.create(
      model="text-davinci-003",
      prompt=f'Write a detailed and informative article about {topic}',
      temperature=0.8,
      max_tokens=600,
      top_p=1.0,
      frequency_penalty=0.5,
      presence_penalty=0.0
    )
  article = response2.choices[0].text
  article_title = article_title.replace('"', '')
  article_intro = ' '.join(re.split(r'(?<=[.:;])\s', article)[:2])
  article_text = ' '.join(re.split(r'(?<=[.:;])\s', article)[2:])
  urls = re.findall(r'(https?://\S+|www\.\S+)', article_text)
  def replace_urls(match):
      url = match.group(0)
      url2 = url
      if not url.startswith("http"):
          url2 = "https://" + url
      return "<a href='" + url2 + "'>" + url + "</a>"
  article_text = re.sub(r'(https?://\S+|www\.\S+)', replace_urls, article_text)
  article_path = re.sub(r'[^a-zA-Z ]+', '', article_title)
  article_path = article_path.replace(' ', '_')
  article_path = article_path.replace('__', '_')
  response = openai.Image.create(
    prompt=article_title,
    n=1,
    size="1024x1024"
  )
  image_url = response['data'][0]['url']
  current_path = fr'{os.path.realpath(__file__).rsplit("/",1)[0]}'
  urllib.request.urlretrieve(image_url, f'{current_path}/assets/images/{article_path}.jpg')
  foo = Image.open(f'{current_path}/assets/images/{article_path}.jpg')
  foo = foo.resize((1000,1000),Image.LANCZOS)
  foo.save(f'{current_path}/assets/images/{article_path}.jpg', optimize=True, quality=85)
  shutil.copyfile(f'{current_path}/template.html', f'{current_path}/articles/{article_path}.html')
  with open(f'{current_path}/articles/{article_path}.html', encoding="utf8") as file :
    filedata = file.read()
  filedata = filedata.replace('[Article title]', article_title)
  filedata = filedata.replace('[Article intro]', article_intro)
  filedata = filedata.replace('[Article text]', article_text)
  filedata = filedata.replace('[image_alt]', article_title)
  filedata = filedata.replace('[image_path]', f'assets/images/{article_path}.jpg')
  filedata = filedata.replace('[Date]', str(date.today()))
  file = codecs.open(f'{current_path}/articles/{article_path}.html', "w", "utf-8")
  file.write(filedata)
  file.close()
  with open(f'{current_path}/index.html', encoding="utf8") as file :
    filedata = file.read()
  filedata = filedata.replace('<!--New article-->', f'''
  <section class="features15 cid-tsOnefHStE" id="features16-1">
      <div class="container">
          <div class="content-wrapper">
              <div class="row align-items-center">
                  <div class="col-12 col-lg">
                      <div class="text-wrapper">
                          <h6 class="card-title mbr-fonts-style display-2">
                              <strong>{article_title}</strong></h6>
                          <p class="mbr-text mbr-fonts-style mb-4 display-4">
                              {article_intro}</p>
                          <div class="mbr-section-btn mt-3"><a class="btn btn-success display-4" href="articles/{article_path}.html">Continue reading</a></div>
                      </div>
                  </div>
                  <div class="col-12 col-lg-6">
                      <div class="image-wrapper">
                          <img src="assets/images/{article_path}.jpg" alt="{article_title}">
                      </div>
                  </div>
              </div>
          </div>
      </div>
  </section>
  <!--New article-->
  ''')
  file = codecs.open(f'{current_path}/index.html', "w", "utf-8")
  file.write(filedata)
  file.close()