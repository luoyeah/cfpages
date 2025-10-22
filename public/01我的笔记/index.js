import { data } from "./data.js"



// DOM元素
const fileListElement = document.getElementById('fileList');
const previewContentElement = document.getElementById('previewContent');
const toggleSidebarButton = document.getElementById('toggleSidebar');
const sidebar = document.querySelector('.sidebar');

// 初始化文件列表
function initFileList() {
    data.files.forEach(file => {
        const li = document.createElement('li');
        li.innerHTML = `
                    <i class="fas ${file.icon}"></i>
                    <span>${file.name}</span>
                `;
        li.dataset.file = file.file;

        li.addEventListener('click', () => {
            // 移除所有active类
            document.querySelectorAll('.file-list li').forEach(item => {
                item.classList.remove('active');
            });

            // 添加active类到当前项
            li.classList.add('active');

            // 加载并渲染Markdown
            setAnchorValue(file.file);
            loadMarkdown(file.file);
        });

        fileListElement.appendChild(li);
    });
}

// 加载并渲染Markdown
function loadMarkdown(filename) {
    fetch(`md/${filename}`)
        .then(response => response.text())
        .then(markdown => {
            previewContentElement.innerHTML = marked.parse(markdown);
        })

}

// 切换侧边栏
toggleSidebarButton.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

// 获取当前URL的锚点部分
function getAnchorValue() {
    let _hash = window.location.hash;
    if (undefined == _hash) return null
    // 移除开头的#号（如果有）
    if (_hash.startsWith('#')) {
        return _hash.substring(1);
    }
    return _hash
}

// 设置新的锚点值
function setAnchorValue(newValue) {
    // 移除开头的#号（如果有）
    if (newValue.startsWith('#')) {
        newValue = newValue.substring(1);
    }

    // 更新URL的锚点部分
    window.location.hash = newValue;

    return newValue;
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    initFileList();


    let Anchor = getAnchorValue()
    if (Anchor) {
        loadMarkdown(Anchor)
    } else {
        // 默认选择第一个文件
        if (data.files.length > 0) {
            const firstFile = document.querySelector('.file-list li');
            if (firstFile) {
                firstFile.click();
            }
        }
    }
});