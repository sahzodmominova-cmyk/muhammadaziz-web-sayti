(function(){
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 3) Kartochkalar skroll paytida chiqadi */
  function setupReveal(){
    if(reduce || !('IntersectionObserver' in window)) return;
    var items = document.querySelectorAll('.course, .test-courses button');
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(!e.isIntersecting) return;
        var el = e.target;
        io.unobserve(el);
        el.classList.add('in');
        setTimeout(function(){ el.classList.remove('reveal','in'); el.style.transitionDelay=''; }, 1100);
      });
    }, {threshold:.12});
    items.forEach(function(el, i){
      el.classList.add('reveal');
      el.style.transitionDelay = ((i % 4) * 90) + 'ms';
      io.observe(el);
    });
  }

  /* 6) Natija balli 0 dan oxirgi qiymatgacha sanaladi */
  function setupScoreCount(){
    var box = document.getElementById('resultScore');
    if(!box || reduce) return;
    var obs;
    function write(txt){ obs.disconnect(); box.textContent = txt; obs.observe(box,{childList:true,characterData:true,subtree:true}); }
    obs = new MutationObserver(function(){
      var m = (box.textContent || '').match(/(\d+)\s*\/\s*(\d+)/);
      if(!m) return;
      var target = +m[1], total = m[2], start = null, dur = 900;
      box.classList.remove('counting'); void box.offsetWidth; box.classList.add('counting');
      function step(ts){
        if(start === null) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        write(Math.round(target * p) + ' / ' + total);
        if(p < 1) requestAnimationFrame(step);
      }
      write('0 / ' + total);
      requestAnimationFrame(step);
    });
    obs.observe(box,{childList:true,characterData:true,subtree:true});
  }

  
  /* Test: savol va raqam almashganda animatsiyani qayta ishga tushirish */
  function retrigger(el, cls){ el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls); }
  function setupQuestionSwap(){
    if(reduce) return;
    ['testQuestion','testNumber'].forEach(function(id){
      var el = document.getElementById(id);
      if(!el) return;
      new MutationObserver(function(){ retrigger(el,'swap'); }).observe(el,{childList:true,characterData:true,subtree:true});
    });
  }

  /* Natija: konfetti (60%+ bo'lsa) va jarima xabari titrashi */
  function confetti(){
    var colors = ['#22d3ee','#667eea','#a78bfa','#facc15','#34d399','#f472b6'];
    for(var i=0;i<70;i++){
      var c = document.createElement('div');
      c.className = 'confetti-piece';
      c.style.left = (Math.random()*100) + 'vw';
      c.style.background = colors[i % colors.length];
      c.style.borderRadius = Math.random() > .5 ? '50%' : '2px';
      c.style.setProperty('--dx', (Math.random()*240-120) + 'px');
      c.style.setProperty('--rot', (Math.random()*720-360) + 'deg');
      c.style.animationDuration = (2.2 + Math.random()*1.8) + 's';
      c.style.animationDelay = (Math.random()*.6) + 's';
      document.body.appendChild(c);
      setTimeout((function(n){ return function(){ n.remove(); }; })(c), 4800);
    }
  }
  function setupResultFx(){
    var res = document.getElementById('testResult');
    if(!res || reduce) return;
    var wasHidden = true;
    new MutationObserver(function(){
      var visible = res.style.display !== 'none';
      if(visible && wasHidden){
        var pct = parseInt((document.getElementById('resultPercent')||{}).textContent, 10) || 0;
        if(pct >= 60) setTimeout(confetti, 500);
      }
      wasHidden = !visible;
    }).observe(res,{attributes:true,attributeFilter:['style']});
    var fine = document.getElementById('resultFine');
    if(fine) new MutationObserver(function(){
      if(fine.style.display !== 'none' && /jarima/i.test(fine.textContent)) retrigger(fine,'shake');
    }).observe(fine,{childList:true,characterData:true,subtree:true});
  }

  document.addEventListener('DOMContentLoaded', function(){ setupReveal(); setupScoreCount(); setupQuestionSwap(); setupResultFx(); });
})();
