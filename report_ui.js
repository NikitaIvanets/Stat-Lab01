(function(){
 const shell=document.querySelector('.report-shell'),sidebar=document.querySelector('.report-sidebar'),menu=document.querySelector('.report-menu'),search=document.querySelector('#report-search'),clear=document.querySelector('.report-clear'),links=[...document.querySelectorAll('.report-nav a')],empty=document.querySelector('.report-nav-empty'),toggle=document.querySelector('.report-subtoggle');
 function setMenu(open){shell.classList.toggle('menu-open',open);menu.setAttribute('aria-expanded',String(open));if(open)search.focus()}
 menu.addEventListener('click',()=>setMenu(!shell.classList.contains('menu-open')));
 document.querySelector('.report-backdrop').addEventListener('click',()=>setMenu(false));
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&shell.classList.contains('menu-open')){setMenu(false);menu.focus()}});
 function filterNav(){let term=search.value.trim().toLocaleLowerCase('ru-RU');sidebar.classList.toggle('is-searching',!!term);clear.hidden=!term;let count=0;for(let a of links){a.hidden=!!term&&!a.textContent.toLocaleLowerCase('ru-RU').includes(term);if(!a.hidden)count++}empty.hidden=count>0;}
 search.addEventListener('input',filterNav);clear.addEventListener('click',()=>{search.value='';filterNav();search.focus()});
 toggle.addEventListener('click',()=>{let show=sidebar.classList.toggle('show-subsections');toggle.setAttribute('aria-expanded',String(show));toggle.textContent=show?'Скрыть подразделы':'Показать все подразделы'});
 const headings=links.map(a=>({link:a,cell:document.getElementById(a.dataset.cell)})).filter(x=>x.cell);
 let pending=false;
 function updatePosition(){pending=false;let active=headings[0];for(let item of headings){if(item.cell.getBoundingClientRect().top<165)active=item;else break}for(let item of headings){let on=item===active;item.link.classList.toggle('active',on);if(on)item.link.setAttribute('aria-current','location');else item.link.removeAttribute('aria-current')}let max=document.documentElement.scrollHeight-innerHeight;document.documentElement.style.setProperty('--report-progress',(max>0?Math.min(100,Math.max(0,scrollY/max*100)):0)+'%');}
 addEventListener('scroll',()=>{if(!pending){pending=true;requestAnimationFrame(updatePosition)}},{passive:true});
 document.addEventListener('click',e=>{let a=e.target.closest('a[href^="#"]');if(!a)return;let id=a.getAttribute('href').slice(1),target=document.getElementById(id);if(!target)return;for(let p=target.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;if(a.closest('.report-nav'))setMenu(false)});
 function resizePlots(){if(!window.Plotly)return;document.querySelectorAll('.js-plotly-plot').forEach(p=>{if(p.clientWidth>0)Plotly.Plots.resize(p)})}
 let resizeTimer;addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(resizePlots,130)});
 addEventListener('load',()=>{updatePosition();resizePlots()},{once:true});updatePosition();
})();
