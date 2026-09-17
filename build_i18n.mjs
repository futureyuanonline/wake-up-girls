// 构建脚本：生成繁体中文版数据文件（node build_i18n.mjs）
import fs from 'fs';
import vm from 'vm';
import { Converter } from 'opencc-js';

const cn2t = Converter({ from: 'cn', to: 'tw' });

function loadData(file) {
  const ctx = { window: {} };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(file, 'utf8'), ctx);
  return ctx.window;
}

function convertDeep(obj) {
  if (typeof obj === 'string') return cn2t(obj);
  if (Array.isArray(obj)) return obj.map(convertDeep);
  if (obj && typeof obj === 'object') {
    const out = {};
    for (const k of Object.keys(obj)) out[k] = convertDeep(obj[k]);
    return out;
  }
  return obj;
}

const issues = loadData('data/issues.js').ISSUES;
const works = loadData('data/works.js').WORKS;

fs.writeFileSync(
  'data/issues.hant.js',
  'window.ISSUES_HANT = ' + JSON.stringify(convertDeep(issues)) + ';',
  'utf8'
);
fs.writeFileSync(
  'data/works.hant.js',
  'window.WORKS_HANT = ' + JSON.stringify(convertDeep(works)) + ';',
  'utf8'
);
console.log('issues.hant.js:', issues.length, '期');
console.log('works.hant.js:', works.length, '条');
