
"use strict";
const fanlar=[
{id:"matematika",nom:"Matematika",emoji:"📐",izoh:"Hisoblash, formulalar va mantiqiy masalalar."},
{id:"informatika",nom:"Informatika",emoji:"💻",izoh:"Kompyuter, algoritmlar va raqamli bilimlar."},
{id:"ingliz",nom:"Ingliz tili",emoji:"🌍",izoh:"Yangi so‘zlar, grammatika va o‘qish."},
{id:"fizika",nom:"Fizika",emoji:"⚛️",izoh:"Tabiat hodisalari va fizik qonunlar."},
{id:"kimyo",nom:"Kimyo",emoji:"🧪",izoh:"Moddalar, reaksiyalar va tajribalar."},
{id:"biologiya",nom:"Biologiya",emoji:"🧬",izoh:"Tirik organizmlar va tabiat olami."},
{id:"tarix",nom:"Tarix",emoji:"🏛️",izoh:"O‘tmish voqealari va tarixiy shaxslar."},
{id:"ona-tili",nom:"Ona tili",emoji:"✍️",izoh:"Imlo, grammatika va nutq madaniyati."},
{id:"adabiyot",nom:"Adabiyot",emoji:"📖",izoh:"Asarlar, adiblar va badiiy tafakkur."},
{id:"geografiya",nom:"Geografiya",emoji:"🗺️",izoh:"Materiklar, davlatlar va geografik xaritalar."},
{id:"iqtisod",nom:"Iqtisod",emoji:"📊",izoh:"Pul, bozor va iqtisodiy fikrlash."},
{id:"huquq",nom:"Huquq",emoji:"⚖️",izoh:"Qonunlar, huquqlar va majburiyatlar."},
{id:"rus-tili",nom:"Rus tili",emoji:"🔤",izoh:"So‘z boyligi va grammatik qoidalar."},
{id:"astronomiya",nom:"Astronomiya",emoji:"🪐",izoh:"Koinot, sayyoralar va yulduzlar."},
{id:"chizmachilik",nom:"Chizmachilik",emoji:"📏",izoh:"Chizmalar va fazoviy tasavvur."},
{id:"mantiq",nom:"Mantiq",emoji:"🧠",izoh:"Fikrlash va muammolarni hal qilish."}
];
const maxsusMavzular={
matematika:[
{nom:"Foizlar",matn:"Foiz — sonning yuzdan bir qismi.\n\nMasalan, 200 ning 10 foizi: 200 × 10 / 100 = 20.\n\nFormula: son × foiz / 100.",savollar:[["100 ning 25 foizi nechaga teng?",["10","20","25","50"],2],["200 ning 10 foizi nechaga teng?",["10","20","30","40"],1],["Foiz nimani bildiradi?",["O‘ndan birni","Yuzdan birni","Mingdan birni","Ikki baravarni"],1]]},
{nom:"Tenglamalar",matn:"Tenglama — noma'lum son qatnashgan tenglik.\n\nMisol: x + 5 = 12. Demak, x = 12 − 5 = 7.\n\nTekshirish: 7 + 5 = 12.",savollar:[["x + 4 = 10 bo‘lsa, x nechaga teng?",["4","5","6","14"],2],["x − 3 = 8 bo‘lsa, x nechaga teng?",["5","11","24","3"],1],["2x = 14 bo‘lsa, x nechaga teng?",["7","12","16","28"],0]]},
{nom:"Geometriya asoslari",matn:"Uchburchakning ichki burchaklari yig‘indisi 180°.\n\nTo‘g‘ri to‘rtburchak yuzi: S = a × b.\nKvadrat yuzi: S = a × a.",savollar:[["Uchburchak burchaklari yig‘indisi?",["90°","180°","270°","360°"],1],["Tomonlari 4 va 5 bo‘lgan to‘g‘ri to‘rtburchak yuzi?",["9","18","20","25"],2],["Kvadratning barcha tomonlari qanday?",["Har xil","Faqat ikkitasi teng","Teng","Parallel emas"],2]]}
],
informatika:[
{nom:"Algoritm tushunchasi",matn:"Algoritm — masalani yechish uchun aniq ketma-ketlikda bajariladigan ko‘rsatmalar.\n\nAsosiy xususiyatlari: aniqlik, tushunarlilik, yakunlanuvchanlik va natijadorlik.",savollar:[["Algoritm nima?",["Kompyuter qurilmasi","Amallar ketma-ketligi","Faqat rasm","Internet manzili"],1],["Algoritm natijasi nima?",["Har doim xato","Yechim yoki natija","Faqat matn","Faqat ovoz"],1],["Algoritm qanday berilishi mumkin?",["Faqat musiqa","Faqat video","Matn yoki blok-sxema","Faqat surat"],2]]},
{nom:"Python asoslari",matn:"Python — dasturlash tili.\n\nprint() ekranga ma'lumot chiqaradi.\ninput() foydalanuvchidan ma'lumot oladi.\n\nMisol:\nism = input('Ismingiz: ')\nprint('Salom,', ism)",savollar:[["Ekranga ma'lumot chiqaruvchi funksiya?",["input()","print()","int()","type()"],1],["Foydalanuvchidan ma'lumot olish uchun?",["print()","str()","input()","range()"],2],["Python’da matn odatda qanday yoziladi?",["Qo‘shtirnoq ichida","Faqat qavsda","Faqat raqam bilan","Nuqtadan keyin"],0]]},
{nom:"O‘zgaruvchilar",matn:"O‘zgaruvchi — qiymatni saqlash uchun ishlatiladigan nom.\n\nMisol:\nyosh = 15\nism = 'Ali'\n\nO‘zgaruvchi nomi ma'noli va bo‘sh joysiz bo‘lishi kerak.",savollar:[["O‘zgaruvchi nima uchun kerak?",["Qiymat saqlash uchun","Monitorni o‘chirish uchun","Internet tezligini oshirish uchun","Faqat rasm chizish uchun"],0],["Qaysi biri to‘g‘ri o‘zgaruvchi nomi?",["mening yoshim","2son","yosh","class"],2],["x = 7 bo‘lsa, x qiymati?",["x","0","7","14"],2]]}
],
ingliz:[
{nom:"To be fe'li",matn:"Ingliz tilida am/is/are — hozirgi zamondagi to be shakllari.\n\nI am a student. — Men o‘quvchiman.\nHe is happy. — U xursand.\nThey are friends. — Ular do‘stlar.",savollar:[["I ___ a student.",["is","are","am","be"],2],["She ___ happy.",["am","is","are","be"],1],["They ___ friends.",["is","am","are","be"],2]]},
{nom:"Oddiy so‘zlar",matn:"Hello — salom.\nBook — kitob.\nSchool — maktab.\nFriend — do‘st.\nLearn — o‘rganmoq.",savollar:[["Book so‘zining tarjimasi?",["Daftar","Kitob","Maktab","Qalam"],1],["Friend nimani anglatadi?",["O‘qituvchi","Oila","Do‘st","Uy"],2],["Hello qanday tarjima qilinadi?",["Xayr","Rahmat","Salom","Iltimos"],2]]}
],
fizika:[{nom:"Tezlik",matn:"Tezlik jismning vaqt birligida bosib o‘tgan yo‘lini bildiradi.\n\nFormula: v = s / t.\nBu yerda v — tezlik, s — yo‘l, t — vaqt.\n\n100 metr yo‘l 20 sekundda bosib o‘tilsa, tezlik 5 m/s.",savollar:[["Tezlik formulasi qaysi?",["v = s / t","s = v / t","t = s × v","v = s × t"],0],["100 metrni 20 sekundda bosib o‘tgan jism tezligi?",["2 m/s","5 m/s","20 m/s","100 m/s"],1],["Tezlik birligi qaysi?",["Kilogramm","Metr","m/s","Sekund"],2]]}],
tarix:[{nom:"Tarixni o‘rganish",matn:"Tarix insoniyatning o‘tmishini o‘rganuvchi fan.\n\nTarixiy manbalar yozma, moddiy va og‘zaki turlarga ajraladi. Arxeologik topilmalar moddiy manbalarga misol bo‘ladi.",savollar:[["Tarix nimani o‘rganadi?",["Faqat tabiatni","Insoniyat o‘tmishini","Faqat matematikani","Faqat tillarni"],1],["Arxeologik topilma qaysi manba?",["Moddiy","Faqat og‘zaki","Faqat elektron","Musiqiy"],0],["Tarixiy voqealar qanday o‘rganiladi?",["Tartibsiz","Vaqt ketma-ketligida","Faqat kelajakdan","Faqat formulada"],1]]}]
};
const umumiyMavzu={nom:"Asosiy tushunchalar",matn:"Bu bo‘lim tanlangan fan bo‘yicha boshlang‘ich tushunchalarni o‘rganish uchun namuna sifatida tayyorlangan.\n\n1. Asosiy atamalarni o‘qing.\n2. Muhim fikrlarni daftarga yozing.\n3. Misollarni mustaqil ishlang.\n4. Test orqali tushunganingizni tekshiring.\n\nEslatma: bu namuna material rasmiy darslik bilan to‘liq mos kelmasligi mumkin.",savollar:[["Yangi mavzuni o‘rganishda nima foydali?",["Matnni o‘qib, misol ishlash","Savollarni o‘qimaslik","Mavzuni tashlab ketish","Faqat taxmin qilish"],0],["Bilimni tekshirish uchun nima qilish mumkin?",["Test ishlash","Darsni yopish","Savolni o‘zgartirish","Hech narsa qilmaslik"],0],["Tushunmagan joyni qanday o‘rganish mumkin?",["Qayta o‘qish va mashq qilish","E'tibor bermaslik","Faqat javobni yodlash","Mavzuni o‘chirish"],0]]};
const sinfTanlash=document.getElementById("sinfTanlash"),chorakTanlash=document.getElementById("chorakTanlash"),qidiruv=document.getElementById("qidiruv"),fanRoyxati=document.getElementById("fanRoyxati"),mavzuPanel=document.getElementById("mavzuPanel"),darsPanel=document.getElementById("darsPanel"),testPanel=document.getElementById("testPanel");
let tanlanganFan="",tanlanganMavzu=null,tanlanganChorak=1,testYakunlangan=false;
let statistika={testlar:0,ball:0,darslar:[]};
try{const s=JSON.parse(localStorage.getItem("edustar_stats")||"{}");statistika.testlar=Number(s.testlar)||0;statistika.ball=Number(s.ball)||0;statistika.darslar=Array.isArray(s.darslar)?s.darslar:[]}catch(e){}
function saqla(){localStorage.setItem("edustar_stats",JSON.stringify(statistika));statistikaniYangila()}
function statistikaniYangila(){document.getElementById("totalTests").textContent=statistika.testlar;document.getElementById("totalPoints").textContent=statistika.ball;document.getElementById("lessonProgressText").textContent=statistika.darslar.length+" ta dars";document.getElementById("lessonProgress").style.width=Math.min(100,statistika.darslar.length/20*100)+"%"}
const yillikMavzuNomlari={
matematika:["Sonlar va amallar","Kasrlar va foizlar","Tenglamalar va ifodalar","Geometriya va o‘lchash"],
informatika:["Kompyuter qurilmalari","Algoritmlar va blok-sxemalar","Dasturlash asoslari","Internet xavfsizligi va loyihalar"],
ingliz:["Kundalik so‘zlar va tanishuv","Hozirgi zamon va gap tuzish","O‘qish va tinglab tushunish","O‘tgan zamon va yozma nutq"],
fizika:["Fizik kattaliklar va o‘lchovlar","Harakat va tezlik","Kuch va energiya","Issiqlik va elektr hodisalari"],
kimyo:["Moddalar va ularning xossalari","Atom va molekula","Kimyoviy reaksiyalar","Eritmalar va kundalik kimyo"],
biologiya:["Tirik organizmlar","Hujayra va uning tuzilishi","O‘simliklar va hayvonlar","Inson organizmi va ekologiya"],
tarix:["Tarixiy manbalar","Qadimgi dunyo tarixi","O‘rta asrlar tarixi","Yangi davr va O‘zbekiston tarixi"],
"ona-tili":["So‘z turkumlari","Gap bo‘laklari","Imlo va tinish belgilari","Matn tuzish va nutq madaniyati"],
adabiyot:["Xalq og‘zaki ijodi","She’riy asarlar","Yozuvchilar va hikoyalar","Badiiy tahlil va ijod"],
geografiya:["Xarita va geografik koordinatalar","Materiklar va okeanlar","Iqlim va tabiiy zonalar","Aholi va mamlakatlar"],
iqtisod:["Ehtiyoj va resurslar","Pul va budjet","Bozor va narx","Tadbirkorlik asoslari"],
huquq:["Huquq va majburiyatlar","Konstitutsiya asoslari","Davlat va qonun","Huquqiy mas’uliyat"],
"rus-tili":["Alifbo va kundalik so‘zlar","Ot va sifat","Fe’l va gap tuzish","Matn o‘qish va yozish"],
astronomiya:["Quyosh tizimi","Sayyoralar va yo‘ldoshlar","Yulduzlar va galaktikalar","Koinot tadqiqotlari"],
chizmachilik:["Chizma asboblari va chiziqlar","Geometrik yasashlar","Proyeksiyalar","Chizma o‘qish va loyiha"],
mantiq:["Mantiqiy ketma-ketliklar","Taqqoslash va tasniflash","Jadvallar va boshqotirmalar","Muammo yechish strategiyalari"]
};
function fanMavzulari(id){
 const mavjud=(maxsusMavzular[id]||[]).map((m,i)=>({...m,fanId:id,mavzuId:id+"-"+i,chorak:i+1}));
 const nomlar=yillikMavzuNomlari[id]||["Asosiy tushunchalar","Amaliy mashqlar","Mustahkamlash","Yakuniy takrorlash"];
 for(let q=1;q<=4;q++){
  if(!mavjud.some(m=>m.chorak===q)){
   const nom=nomlar[q-1];
   mavjud.push({...umumiyMavzu,nom,matn:`${nom} — ${fanlar.find(f=>f.id===id)?.nom||"fan"} bo‘yicha o‘quv mavzusi.\n\n1. Mavzuning asosiy tushunchalarini o‘rganing.\n2. Muhim atamalarni yozib oling.\n3. O‘rganganlaringizni misollar orqali mashq qiling.\n4. Quyidagi test bilan bilimingizni tekshiring.\n\nEslatma: bu boshlang‘ich namuna materialidir; sinfingiz darsligiga mos qo‘shimcha materiallar o‘qituvchi tomonidan kiritilishi mumkin.`,fanId:id,mavzuId:id+"-yillik-"+q,chorak:q});
  }
 }
 return mavjud.sort((a,b)=>a.chorak-b.chorak);
}
function fanlarniChiz(){const q=qidiruv.value.trim().toLocaleLowerCase("uz");const royxat=fanlar.filter(f=>f.nom.toLocaleLowerCase("uz").includes(q)||f.izoh.toLocaleLowerCase("uz").includes(q));fanRoyxati.innerHTML="";if(!royxat.length){fanRoyxati.textContent="Bu nomda fan topilmadi.";return}royxat.forEach(f=>{const el=document.createElement("article");el.className="subject";el.innerHTML=`<div class="emoji">${f.emoji}</div><h3>${f.nom}</h3><p>${f.izoh}</p><button class="btn secondary" type="button">Fan haqida →</button>`;el.querySelector("button").addEventListener("click",()=>fanTanla(f.id));fanRoyxati.appendChild(el)})}
function fanTanla(id){tanlanganFan=id;const f=fanlar.find(x=>x.id===id);if(!f)return;document.getElementById("fanSarlavha").textContent=f.emoji+" "+f.nom;document.getElementById("fanTavsif").textContent=f.izoh;mavzuPanel.classList.remove("hidden");darsPanel.classList.add("hidden");testPanel.classList.add("hidden");mavzularniChiz();mavzuPanel.scrollIntoView({behavior:"smooth",block:"start"})}
function mavzularniChiz(){const el=document.getElementById("mavzularRoyxati");el.innerHTML="";if(!tanlanganFan)return;const ms=fanMavzulari(tanlanganFan).filter(m=>m.chorak===tanlanganChorak);if(!ms.length){el.textContent="Bu chorak uchun mavzu hali qo‘shilmagan. Boshqa chorakni tanlang.";return}ms.forEach(m=>{const done=statistika.darslar.includes(darsKaliti(m));const card=document.createElement("div");card.className="topic";card.innerHTML=`<div><h4>${m.nom}</h4><p class="small">${done?"✓ Tugatilgan":"Dars va test mavjud"}</p></div><button class="btn" type="button">Ochish</button>`;card.querySelector("button").addEventListener("click",()=>darsniOch(m));el.appendChild(card)})}
function darsKaliti(m){return m.fanId+":"+m.mavzuId}
function darsniOch(m){tanlanganMavzu=m;testYakunlangan=false;document.getElementById("darsSarlavha").textContent=m.nom;document.getElementById("darsMeta").textContent=sinfTanlash.value+"-sinf · "+chorakTanlash.value+"-chorak";document.getElementById("darsMatni").textContent=m.matn;document.getElementById("markLesson").textContent=statistika.darslar.includes(darsKaliti(m))?"✓ Dars tugatilgan":"✓ Darsni tugatdim";document.getElementById("lessonNotice").style.display="none";mavzuPanel.classList.add("hidden");testPanel.classList.add("hidden");darsPanel.classList.remove("hidden");darsPanel.scrollIntoView({behavior:"smooth",block:"start"})}
function testniBoshlash(){if(!tanlanganMavzu){alert("Avval mavzuni tanlang.");return}testYakunlangan=false;document.getElementById("testSarlavha").textContent="📝 "+tanlanganMavzu.nom;document.getElementById("testMeta").textContent="Har bir to‘g‘ri javob uchun 10 ball.";const list=document.getElementById("savollarRoyxati");list.innerHTML="";tanlanganMavzu.savollar.forEach((s,i)=>{const b=document.createElement("div");b.className="quiz-question";const h=document.createElement("h4");h.textContent=(i+1)+". "+s[0];b.appendChild(h);s[1].forEach((v,j)=>{const l=document.createElement("label");l.className="answer";const inp=document.createElement("input");inp.type="radio";inp.name="savol_"+i;inp.value=j;inp.required=true;const span=document.createElement("span");span.textContent=v;l.append(inp,span);b.appendChild(l)});list.appendChild(b)});document.getElementById("quizResult").classList.add("hidden");document.getElementById("quizResult").innerHTML="";document.getElementById("submitTest").disabled=false;darsPanel.classList.add("hidden");mavzuPanel.classList.add("hidden");testPanel.classList.remove("hidden");testPanel.scrollIntoView({behavior:"smooth",block:"start"})}
function natijaniTekshir(event){event.preventDefault();if(!tanlanganMavzu||testYakunlangan)return;const form=document.getElementById("quizForm");if(!form.reportValidity())return;let togri=0;const savollar=tanlanganMavzu.savollar,bloklar=document.querySelectorAll(".quiz-question");savollar.forEach((s,i)=>{const tanlov=form.querySelector(`input[name="savol_${i}"]:checked`);if(!tanlov)return;const javob=Number(tanlov.value),togrisi=s[2];bloklar[i].querySelectorAll(".answer").forEach((label,j)=>{label.classList.remove("correct","wrong");if(j===togrisi)label.classList.add("correct");if(j===javob&&javob!==togrisi)label.classList.add("wrong");label.querySelector("input").disabled=true});if(javob===togrisi)togri++});testYakunlangan=true;const jami=savollar.length,foiz=jami?Math.round(togri/jami*100):0,yangiBall=togri*10;statistika.testlar++;statistika.ball+=yangiBall;saqla();const n=document.getElementById("quizResult");n.classList.remove("hidden");n.innerHTML=`<h3>🏆 Test natijasi</h3><p>To‘g‘ri javoblar: <strong>${togri}/${jami}</strong></p><p>Natija: <strong>${foiz}%</strong></p><p>To‘plangan ball: <strong>+${yangiBall}</strong></p><p>${foiz>=80?"Ajoyib! Mavzuni yaxshi o‘zlashtirgansiz.":foiz>=50?"Yaxshi! Xatolarni ko‘rib, yana mashq qiling.":"Mavzuni qayta o‘qib, testni yana ishlang."}</p>`;document.getElementById("submitTest").disabled=true;n.scrollIntoView({behavior:"smooth",block:"center"})}
document.getElementById("quizForm").addEventListener("submit",natijaniTekshir);
document.getElementById("resetTest").addEventListener("click",testniBoshlash);
document.getElementById("startTest").addEventListener("click",testniBoshlash);
document.getElementById("markLesson").addEventListener("click",()=>{if(!tanlanganMavzu)return;const k=darsKaliti(tanlanganMavzu);if(!statistika.darslar.includes(k)){statistika.darslar.push(k);saqla()}document.getElementById("markLesson").textContent="✓ Dars tugatilgan";const n=document.getElementById("lessonNotice");n.textContent="🎉 Dars tugatilgan deb belgilandi!";n.style.display="block";mavzularniChiz()});
document.getElementById("backSubjects").addEventListener("click",()=>{mavzuPanel.classList.add("hidden");darsPanel.classList.add("hidden");testPanel.classList.add("hidden");document.getElementById("fanlar").scrollIntoView({behavior:"smooth"})});
document.getElementById("backTopics").addEventListener("click",()=>{darsPanel.classList.add("hidden");testPanel.classList.add("hidden");mavzuPanel.classList.remove("hidden");mavzularniChiz();mavzuPanel.scrollIntoView({behavior:"smooth",block:"start"})});
document.getElementById("backLesson").addEventListener("click",()=>{testPanel.classList.add("hidden");darsPanel.classList.remove("hidden");darsPanel.scrollIntoView({behavior:"smooth",block:"start"})});
sinfTanlash.addEventListener("change",()=>{mavzuPanel.classList.add("hidden");darsPanel.classList.add("hidden");testPanel.classList.add("hidden");fanlarniChiz()});
chorakTanlash.addEventListener("change",()=>{tanlanganChorak=Number(chorakTanlash.value);if(tanlanganFan)mavzularniChiz()});
qidiruv.addEventListener("input",fanlarniChiz);
document.getElementById("themeBtn").addEventListener("click",()=>{document.body.classList.toggle("light");localStorage.setItem("edustar_theme",document.body.classList.contains("light")?"light":"dark")});
if(localStorage.getItem("edustar_theme")==="light")document.body.classList.add("light");
document.getElementById("year").textContent=new Date().getFullYear();fanlarniChiz();statistikaniYangila();


/* Dekorativ harakatlanuvchi yulduzchalar va ekranga kirish animatsiyasi */
document.addEventListener('DOMContentLoaded',()=>{
  const reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(!reduced){
    const symbols=['✦','✧','·','✶'];
    for(let i=0;i<22;i++){
      const star=document.createElement('span');star.className='edustar-star';star.textContent=symbols[i%symbols.length];
      star.style.left=(3+Math.random()*94)+'vw';star.style.top=(8+Math.random()*86)+'vh';
      star.style.setProperty('--duration',(7+Math.random()*11)+'s');star.style.setProperty('--size',(7+Math.random()*12)+'px');star.style.setProperty('--opacity',(0.25+Math.random()*0.55).toFixed(2));
      star.style.animationDelay=(-Math.random()*12)+'s';document.body.appendChild(star);
    }
    const items=document.querySelectorAll('.subject,.feature,.panel,.hero-card');
    if('IntersectionObserver' in window){
      const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('reveal-on-scroll');observer.unobserve(entry.target)}}),{threshold:.08});
      items.forEach(el=>observer.observe(el));
    }
  }
});
