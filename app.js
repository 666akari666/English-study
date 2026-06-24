// 全局状态记录
let currentArticleText = "";
let synth = window.speechSynthesis;
let utterance = null;

document.addEventListener("DOMContentLoaded", () => {
    loadHistoryList();
    initWordLookup();
    initTTS();
});

// 1. 加载历史文章列表
async function loadHistoryList() {
    try {
        const response = await fetch('data/index.json');
        if (!response.ok) throw new Error('无法读取索引数据');
        const list = await response.json();
        
        const listContainer = document.getElementById('history-list');
        listContainer.innerHTML = '';

        if(list.length === 0) {
            listContainer.innerHTML = '<li>暂无文章</li>';
            return;
        }

        list.forEach((item, index) => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="date">${item.date}</span> ${item.title}`;
            li.addEventListener('click', () => {
                // 切换激活状态样式
                document.querySelectorAll('#history-list li').forEach(el => el.classList.remove('active'));
                li.classList.add('active');
                // 加载具体文章内容
                loadArticle(item.date);
            });
            listContainer.appendChild(li);

            // 默认加载最新的一篇文章
            if (index === 0) {
                li.classList.add('active');
                loadArticle(item.date);
            }
        });
    } catch (err) {
        document.getElementById('history-list').innerHTML = `<li>加载失败: ${err.message}</li>`;
    }
}

// 2. 加载指定日期文章详情
async function loadArticle(date) {
    // 停止正在播放的朗读
    stopReading();

    try {
        const response = await fetch(`data/articles/${date}.json`);
        if (!response.ok) throw new Error('无法读取文章详情');
        const article = await response.json();

        document.getElementById('article-date').innerText = article.date;
        document.getElementById('article-source').innerText = article.source;
        document.getElementById('article-title').innerText = article.title;
        
        // 解析正文换行符并渲染
        const bodyContainer = document.getElementById('article-body');
        const paragraphs = article.content.split('\n\n');
        bodyContainer.innerHTML = paragraphs.map(p => `<p>${p}</p>`).join('');

        // 记录文本用于语音朗读
        currentArticleText = `${article.title}. ${article.content}`;
    } catch (err) {
        document.getElementById('article-body').innerHTML = `<p style="color:red;">文章加载失败: ${err.message}</p>`;
    }
}

// 3. 语音朗读功能 (TTS)
function initTTS() {
    const btnPlay = document.getElementById('btn-tts');
    const btnStop = document.getElementById('btn-tts-stop');

    btnPlay.addEventListener('click', () => {
        if (!currentArticleText) return;

        if (synth.speaking) {
            synth.cancel(); // 如果正在朗读，先停止
        }

        utterance = new SpeechSynthesisUtterance(currentArticleText);
        utterance.lang = 'en-US'; // 设置为美音（也可以设为 en-GB 英音）
        utterance.rate = 0.9;     // 语速稍放慢一点，适合学习

        utterance.onend = () => {
            btnPlay.style.display = 'inline-block';
            btnStop.style.display = 'none';
        };

        synth.speak(utterance);
        btnPlay.style.display = 'none';
        btnStop.style.display = 'inline-block';
    });

    btnStop.addEventListener('click', stopReading);
}

function stopReading() {
    if (synth && synth.speaking) {
        synth.cancel();
    }
    const btnPlay = document.getElementById('btn-tts');
    const btnStop = document.getElementById('btn-tts-stop');
    if (btnPlay && btnStop) {
        btnPlay.style.display = 'inline-block';
        btnStop.style.display = 'none';
    }
}

// 4. 双击取词翻译
function initWordLookup() {
    const popup = document.getElementById('dict-popup');
    const wordSpan = document.getElementById('selected-word');
    const btnLookup = document.getElementById('btn-lookup');

    document.addEventListener('dblclick', (e) => {
        const selection = window.getSelection().toString().trim();
        // 确保选中的是一个英文单词
        if (selection && /^[a-zA-Z'-]+$/.test(selection)) {
            wordSpan.innerText = selection;
            
            // 定位弹窗在鼠标双击位置附近
            popup.style.left = `${e.pageX}px`;
            popup.style.top = `${e.pageY + 15}px`;
            popup.style.display = 'block';

            // 绑定词典跳转链接
            btnLookup.onclick = () => {
                window.open(`https://dict.youdao.com/w/${selection}`, '_blank');
                popup.style.display = 'none';
            };
        } else {
            popup.style.display = 'none';
        }
    });

    // 点击其他地方关闭弹窗
    document.addEventListener('click', (e) => {
        if (!popup.contains(e.target)) {
            popup.style.display = 'none';
        }
    });
}