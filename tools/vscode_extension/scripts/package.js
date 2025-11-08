const fs = require('fs');
const path = require('path');
const archiver = require('archiver');

// 创建 dist 目录
const distDir = path.join(__dirname, '../dist');
if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
}

// VSIX 文件路径
const vsixPath = path.join(distDir, 'objwatch-visualizer-1.0.0.vsix');

// 创建输出流
const output = fs.createWriteStream(vsixPath);
const archive = archiver('zip', {
    zlib: { level: 9 } // 最大压缩
});

// 监听归档完成事件
output.on('close', function() {
    console.log(`VSIX 文件已创建: ${vsixPath}`);
    console.log(`文件大小: ${(archive.pointer() / 1024 / 1024).toFixed(2)} MB`);
});

archive.on('error', function(err) {
    throw err;
});

// 管道输出
archive.pipe(output);

// 添加 package.json
archive.file(path.join(__dirname, '../package.json'), { name: 'extension/package.json' });

// 添加编译后的文件
const outDir = path.join(__dirname, '../out');
if (fs.existsSync(outDir)) {
    archive.directory(outDir, 'extension/out');
}

// 添加媒体文件
const mediaDir = path.join(__dirname, '../media');
if (fs.existsSync(mediaDir)) {
    archive.directory(mediaDir, 'extension/media');
}

// 添加 README
archive.file(path.join(__dirname, '../README.md'), { name: 'extension/README.md' });

// 添加文档
const docsDir = path.join(__dirname, '../docs');
if (fs.existsSync(docsDir)) {
    archive.directory(docsDir, 'extension/docs');
}

// 完成归档
archive.finalize();