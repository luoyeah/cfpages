export let categories = [];

// 获取hostname
const hostname = window.location.hostname;
const url_prefix = `https://${hostname}`;

// --- 分类 1: 内部网络应用 ---
categories.push({
    name: "手机应用",
    links: [
        { name: "页面二维码", url: "04网站地址/index.html" },
        { name: "资源管理器", url: `${url_prefix}:8001` },
        { name: "文件同步", url: `${url_prefix}:8021` },
        { name: "文件服务", url: `${url_prefix}:8011` },
        { name: "文件服务(IE)", url: `http://${hostname}:8002`}
    ]
});

// --- 分类 2: 本地工具/项目 ---
categories.push({
    name: "本地工具",
    links: [
        { name: "我的笔记", url: "01我的笔记/index.html" },
        { name: "全屏省电", url: "02全屏省电/index.html" },
        { name: "位置记录器", url: "/main.html" }
    ]
});

// --- 分类 3: 外部常用链接 ---
categories.push({
    name: "外部常用链接",
    links: [
        { name: "Scoop", url: "https://scoop.sh/" }
    ]
});

export default {}