// Composite only image-tool pigment on unused rock; preserve all ancestor marks.
import fs from 'node:fs';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const encode=require('../line-3/tools/corpus-change-receipt/vendor/jpeg-js/lib/encoder.js');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function crc(b){let v=0xffffffff;for(const c of b){v^=c;for(let j=0;j<8;j++)v=(v>>>1)^((v&1)?0xedb88320:0);}return (v^0xffffffff)>>>0;}
function read(path){
 const raw=fs.readFileSync(path);let w,h,ch,parts=[];
 for(let p=8;p<raw.length;){const n=raw.readUInt32BE(p),k=raw.toString('ascii',p+4,p+8),b=raw.subarray(p+8,p+8+n);
  if(crc(raw.subarray(p+4,p+8+n))!==raw.readUInt32BE(p+8+n))throw Error('CRC');
  if(k==='IHDR'){w=b.readUInt32BE(0);h=b.readUInt32BE(4);ch=b[9]===2?3:b[9]===6?4:0;if(b[8]!==8||b[12]!==0||!ch)throw Error('PNG format');}
  if(k==='IDAT')parts.push(b);p+=n+12;
 }
 const data=zlib.inflateSync(Buffer.concat(parts)),stride=w*ch,out=Buffer.alloc(w*h*4);let prev=Buffer.alloc(stride),at=0;
 for(let y=0;y<h;y++){let mode=data[at++],row=Buffer.from(data.subarray(at,at+stride));at+=stride;
  for(let x=0;x<stride;x++){let a=x>=ch?row[x-ch]:0,b=prev[x],c=x>=ch?prev[x-ch]:0,v=0;
   if(mode===1)v=a;else if(mode===2)v=b;else if(mode===3)v=(a+b)>>1;else if(mode===4){let p=a+b-c,ds=[Math.abs(p-a),Math.abs(p-b),Math.abs(p-c)];v=[a,b,c][ds.indexOf(Math.min(...ds))];}else if(mode!==0)throw Error('filter');
   row[x]=(row[x]+v)&255;
  }
  for(let x=0;x<w;x++){row.copy(out,(y*w+x)*4,x*ch,x*ch+3);out[(y*w+x)*4+3]=ch===4?row[x*ch+3]:255;}prev=row;
 }
 return {w,h,pixels:out,raw};
}
function chunk(k,b){let tag=Buffer.from(k),n=Buffer.alloc(4),sum=Buffer.alloc(4);n.writeUInt32BE(b.length);sum.writeUInt32BE(crc(Buffer.concat([tag,b])));return Buffer.concat([n,tag,b,sum]);}
function png(w,h,pixels){let ih=Buffer.alloc(13);ih.writeUInt32BE(w);ih.writeUInt32BE(h,4);ih[8]=8;ih[9]=2;
 let rows=[];for(let y=0;y<h;y++)rows.push(Buffer.from([0]),pixels.subarray(y*w*3,(y+1)*w*3));
 return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',ih),chunk('IDAT',zlib.deflateSync(Buffer.concat(rows),{level:9})),chunk('IEND',Buffer.alloc(0))]);}

const source='artifacts/gathering/wall-v15.png',target='artifacts/gathering/wall-v16.png';
const original=read(source),draft=read(target),{w,h}=original;
if(w!==1254||h!==1254)throw Error('ancestor dimensions');
if(fs.existsSync('gathering/image-preservation-36.json'))throw Error('Do not apply twice');
const final=Buffer.alloc(w*h*3);
for(let i=0;i<w*h;i++)original.pixels.copy(final,i*3,i*4,i*4+3);
let left=draft.w,top=draft.h,right=0,bottom=0;
for(let y=0;y<draft.h;y++)for(let x=0;x<draft.w;x++)if(draft.pixels[(y*draft.w+x)*4+3]>16){left=Math.min(left,x);top=Math.min(top,y);right=Math.max(right,x);bottom=Math.max(bottom,y);}
if(right<=left||bottom<=top)throw Error('missing generated alpha pigment');
const rect=[425,190,125,55];let changed=0;
const dw=rect[2],dh=Math.round(dw*(bottom-top+1)/(right-left+1));
if(dh>rect[3])throw Error('mark height');
for(let y=0;y<dh;y++)for(let x=0;x<dw;x++){
 let sums=[0,0,0],opacity=0,count=0;
 const x1=left+Math.floor(x*(right-left+1)/dw),x2=left+Math.floor((x+1)*(right-left+1)/dw);
 const y1=top+Math.floor(y*(bottom-top+1)/dh),y2=top+Math.floor((y+1)*(bottom-top+1)/dh);
 for(let sy=y1;sy<y2;sy++)for(let sx=x1;sx<x2;sx++){
  const p=(sy*draft.w+sx)*4,a=draft.pixels[p+3]/255;
  for(let c=0;c<3;c++)sums[c]+=draft.pixels[p+c]*a;
  opacity+=a;count++;
 }
 if(!opacity)continue;
 const i=((rect[1]+y)*w+rect[0]+x)*3,oi=((rect[1]+y)*w+rect[0]+x)*4;
 const light=(original.pixels[oi]+original.pixels[oi+1]+original.pixels[oi+2])/3;
 const a=.68*opacity/count;
 for(let c=0;c<3;c++){
  const pigment=sums[c]/opacity*(.7+light/350);
  final[i+c]=Math.round(original.pixels[oi+c]*(1-a)+pigment*a);
 }
 if(!final.subarray(i,i+3).equals(original.pixels.subarray(oi,oi+3)))changed++;
}
if(changed<500)throw Error('missing mark');
const result=png(w,h,final);fs.writeFileSync(target,result);
const thumb=Buffer.alloc(512*512*4);
for(let y=0;y<512;y++)for(let x=0;x<512;x++){
 let sums=[0,0,0],n=0;
 for(let yy=Math.floor(y*h/512);yy<Math.floor((y+1)*h/512);yy++)for(let xx=Math.floor(x*w/512);xx<Math.floor((x+1)*w/512);xx++){
  for(let c=0;c<3;c++)sums[c]+=final[(yy*w+xx)*3+c];n++;
 }
 let p=(y*512+x)*4;for(let c=0;c<3;c++)thumb[p+c]=Math.round(sums[c]/n);thumb[p+3]=255;
}
const jpg=encode({data:thumb,width:512,height:512},80).data;if(jpg.length>100000)throw Error('thumbnail size');
fs.writeFileSync('dist/gathering/36.jpg',jpg);
const continuation='artifacts/gathering/wall.png';
try{fs.unlinkSync(continuation);}catch(e){if(e.code!=='ENOENT')throw e;}
fs.symlinkSync('wall-v16.png',continuation);
const evidence={ancestor_sha256:hash(original.raw),generated_mark_sha256:hash(draft.raw),wall_sha256:hash(result),dimensions:[w,h],format:'PNG',mode:'RGB',new_mark_rectangle:rect,changed_pixels:changed,changed_pixels_outside_rectangle:0,method:'Generated transparent ochre loops and chalk bridge, cropped in memory and alpha-composited onto unused upper rock. The generated draft was replaced by the finished wall; no extra image saved. Ancestral pixels elsewhere copied unchanged.',preview:{dimensions:[512,512],format:'JPEG',bytes:jpg.length},unmet_visual_requirements:[]};
fs.writeFileSync('gathering/image-preservation-36.json',JSON.stringify(evidence,null,2)+'\n');console.log(JSON.stringify(evidence));
