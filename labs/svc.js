
let buf="";process.stdin.on("data",d=>buf+=d).on("end",()=>{
  const o=JSON.parse(buf);
  const out={ tien:Number(o.tien), emoji:o.emoji, ngay_dst:new Date(o.ngay_dst).toISOString(), rong:o.rong };
  console.log(JSON.stringify(out));
});