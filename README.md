## Auto-Spacing

Sublime Text 3 插件，给中英文之间加上空格。

为什么你们就是不能加个空格呢，为什么我就是能这样娴熟地加上空格呢。

[English](./README-EN.md)

## 安装

### 通过 git

git clone 这个仓库到 Sublime Text 3 的插件目录下 (Mac 的目录 ~/Library/Application Support/Sublime Text 3/Packages/)。

### 通过 sublime 控制台

`Ctrl + Shift + P` 选择  `Auto-Spacing`。

** 还没有被 merge，暂时还不能通过控制台下载 **

## Commands
**Command palette:**

- Auto-Spacing: Spacing this file

**Shortcut key:**

* Linux/Windows: [Ctrl + Shift + B]
* Mac: [Cmd + Shift + B]


## Settings

默认设置:

```javascript
{
  "format_on_save_extensions": false,
  [
    "md",
    "txt"
  ]
}
```

* 可自行更改默认设置 `Preferences -> Package Settings -> Auto-Spacing -> Settings - User`。

## Contributing

欢迎提交 PR。

## Thanks

[@vinta](https://github.com/vinta/pangu.py)

## License

MIT
