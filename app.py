import matplotlib
import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

# 设置字体，确保支持中文
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['STHeiti']  # 指定默认字体
matplotlib.rcParams['axes.unicode_minus'] = False

# 1. 获取网页文本内容
def fetch_text_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        return text
    except Exception as e:
        return str(e)

# 2. 分词和词频统计
def get_word_frequency(text):
    # 使用jieba进行中文分词
    words = jieba.cut(text)
    words = [word for word in words if len(word) > 1]  # 去除单字
    word_counts = Counter(words)  # 统计词频
    return word_counts

# 3. 生成并展示词云
def generate_wordcloud(word_counts):
    wordcloud = WordCloud(font_path='Fonts/STIXNonUni.ttf', width=800, height=600).generate_from_frequencies(word_counts)

    # 创建一个新的图形
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # 不显示坐标轴

    # 保存到缓冲区并返回
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # 关闭当前图形以释放内存
    buf.seek(0)  # 将指针移动到缓冲区的开始
    return buf

# 4. 绘制瀑布图
def plot_waterfall(data):
    labels, values = zip(*data)
    fig, ax = plt.subplots()
    ax.stackplot(labels, values)
    plt.xticks(rotation=90)
    st.pyplot(fig)

# Streamlit应用
if __name__ == "__main__":
    st.title("文章词频分析与词云展示")

    # 用户输入URL
    url = st.text_input("请输入文章URL:", "")

    if url:
        # 获取网页文本内容
        text = fetch_text_from_url(url)

        if "Error" in text:
            st.error("无法抓取该页面，请检查URL是否正确")
        else:
            st.subheader("抓取的文章内容")
            st.write(text[:1000])  # 输出前1000个字符

            # 词频统计
            word_counts = get_word_frequency(text)
            most_common_words = word_counts.most_common(20)

            # 词频排名前20
            st.subheader("词频排名前20的词汇")
            st.write(most_common_words)

            # 图表类型筛选
            chart_type = st.sidebar.selectbox("选择图表类型",
                                              ["词云图", "柱状图", "饼图", "条形图", "折线图", "散点图", "瀑布图"])

            # 绘制不同类型的图表
            if chart_type == "词云图":
                wordcloud_buf = generate_wordcloud(word_counts)
                st.image(wordcloud_buf)
            elif chart_type == "柱状图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.bar(labels, values)
                plt.xticks(rotation=90)
                st.pyplot(fig)
            elif chart_type == "饼图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.pie(values, labels=labels, autopct='%1.1f%%')
                st.pyplot(fig)
            elif chart_type == "条形图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.barh(labels, values)
                st.pyplot(fig)
            elif chart_type == "折线图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.plot(labels, values)
                plt.xticks(rotation=90)
                st.pyplot(fig)
            elif chart_type == "散点图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.scatter(labels, values)
                plt.xticks(rotation=90)
                st.pyplot(fig)
            elif chart_type == "瀑布图":
                data = list(most_common_words)
                plot_waterfall(data)

            # 交互式词频过滤
            st.subheader("交互式词频过滤")
            min_frequency = st.slider("选择最小频率", min_value=1, max_value=max(word_counts.values()), value=1)
            filtered_words = {word: count for word, count in word_counts.items() if count >= min_frequency}
            st.write(filtered_words)