import matplotlib.pyplot as plt

x = [1, 3, 5, 10]
y1 = [40.92, 58.28, 63.67, 68.66]
y2 = [41.92, 60.68, 66.07, 71.06]
y3 = [72.26, 82.04, 84.63] # added data

plt.plot(x, y1, 'o-', label='sina_news_gbk (binary)') # modified label
plt.plot(x, y2, 'o-', label='sina_news_gbk + baike_qa2019 (binary)') # modified label
plt.plot(x[:3], y3, 'o-', label='sina_news_gbk (triple)') # added plot
plt.xticks(range(1, 11))
for i in range(len(x)):
    plt.text(x[i]+0.1, y1[i]-3 if i > 0 else y1[i]-2, str(y1[i]) + '%', ha='center', va='bottom')
    plt.text(x[i]-0.1, y2[i]+3, str(y2[i]) + '%', ha='center', va='top')
    if i < 3:
        plt.text(x[i]+0.1, y3[i], str(y3[i]) + '%', ha='center', va='bottom') # added text
plt.xlabel('Top k')
plt.ylabel('Top k Sentence Accuracy (%)')
plt.legend()
plt.show()