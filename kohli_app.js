(function(){
  function _x(){
    document.body.innerHTML='<div style="background:#000;color:#f44;font-family:monospace;display:flex;height:100vh;align-items:center;justify-content:center;font-size:18px;">Connection lost.</div>';
  }
  document.addEventListener('keydown',function(e){
    if(e.key==='F12'){e.preventDefault();_x();}
    if(e.ctrlKey&&e.shiftKey&&'IJCijc'.includes(e.key)){e.preventDefault();_x();}
    if(e.ctrlKey&&'Uu'.includes(e.key)){e.preventDefault();}
  },true);
  document.addEventListener('contextmenu',function(e){e.preventDefault();});
  setInterval(function(){
    if(window.outerWidth-window.innerWidth>160||window.outerHeight-window.innerHeight>160)_x();
  },1000);
})();

var _o=document.getElementById('out');
var _i=document.getElementById('inp');
var _busy=false;

function _sl(ms){return new Promise(function(r){setTimeout(r,ms);});}

function _add(text,cls){
  var d=document.createElement('div');
  d.className='ln '+(cls||'');
  d.innerHTML=text;
  _o.appendChild(d);
  _o.scrollTop=_o.scrollHeight;
}

function _blank(){
  var d=document.createElement('div');
  d.className='blank';
  _o.appendChild(d);
  _o.scrollTop=_o.scrollHeight;
}

function _esc(t){
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function _prompt(cmd){
  return '<span class="pu">kaalchakra</span>'
       +'<span class="pa">@</span>'
       +'<span class="ph">ctf</span>'
       +'<span class="pk">:</span>'
       +'<span class="pp">~</span>'
       +'<span class="pd">$</span>'
       +' '+_esc(cmd);
}

function _tw(text,cls,spd){
  return new Promise(function(resolve){
    var d=document.createElement('div');
    d.className='ln '+(cls||'');
    _o.appendChild(d);
    var i=0;
    function t(){
      if(i<text.length){
        d.textContent+=text[i++];
        _o.scrollTop=_o.scrollHeight;
        setTimeout(t,spd||18);
      } else resolve();
    }
    t();
  });
}

async function _run(){
  if(_busy)return;
  var v=_i.value;
  if(!v.trim())return;
  _busy=true;
  _i.value='';

  _add(_prompt(v),'cmd');
  await _sl(80);
  _add('[SYS] Processing...','sys');
  await _sl(300+Math.random()*150);

  try{
    var r=await fetch('/run',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({cmd:v.trim()})
    });
    var d=await r.json();
    var out=(d.output||'').trim();

    if(out.startsWith('FLAG{')){
      _blank();
      await _tw('[SYS] '+out,'flag',26);
      _add('[SYS] Frequency phantom decoded successfully.','sys');
      _blank();
    } else if(out.startsWith('[ERR]')){
      _add('[SYS] \u2192 '+_esc(out),'err');
    } else if(out){
      _add('[SYS] \u2192 '+_esc(out),'res');
    } else {
      _add('[SYS] \u2192 no output','res');
    }
  } catch(e){
    _add('[SYS] connection error','err');
  }

  _busy=false;
  _i.focus();
}

_i.addEventListener('keydown',function(e){
  if(e.key==='Enter')_run();
});
document.addEventListener('click',function(){_i.focus();});

// boot
(async function(){
  _add('[SYS] Kaalchakra node online.','sys');
  await _sl(40);
  _add('[SYS] Stream ready.','sys');
  await _sl(40);
  _blank();
  _i.focus();
})();


document.addEventListener('contextmenu', e => e.preventDefault());

['copy', 'cut', 'paste'].forEach(event => {
  document.addEventListener(event, e => e.preventDefault());
});

document.addEventListener('selectstart', e => e.preventDefault());

document.addEventListener('dragstart', e => e.preventDefault());

document.addEventListener('keydown', function(e) {
  if (e.ctrlKey || e.metaKey) {
    const blockedKeys = ['c', 'v', 'x', 'a', 's', 'u', 'p'];
    if (blockedKeys.includes(e.key.toLowerCase())) {
      e.preventDefault();
    }
  }

  if (e.key === 'F12') {
    e.preventDefault();
  }

  if (e.ctrlKey && e.shiftKey && ['I','J','C'].includes(e.key)) {
    e.preventDefault();
  }
});

setInterval(() => {
  debugger;
}, 100);