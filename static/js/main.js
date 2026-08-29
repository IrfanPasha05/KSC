// Sticky header state
const header = document.getElementById('siteHeader');
const onScroll = () => {
  if (window.scrollY > 40) header.classList.add('scrolled');
  else header.classList.remove('scrolled');
};
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Mobile menu toggle
const menuToggle = document.getElementById('menuToggle');
const navLinks = document.querySelector('.nav-links');
menuToggle.addEventListener('click', () => {
  const isOpen = navLinks.style.display === 'flex';
  navLinks.style.cssText = isOpen
    ? ''
    : 'display:flex;position:absolute;top:100%;left:0;right:0;flex-direction:column;background:rgba(14,38,36,.97);padding:22px 28px;gap:18px;border-top:1px solid rgba(255,209,102,.2);';
});

// Reveal on scroll
const revealEls = document.querySelectorAll('.reveal, .cat-card');
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('in');
      io.unobserve(e.target);
    }
  });
}, { threshold: 0.15 });
revealEls.forEach(el => io.observe(el));

// Cut explorer tabs — data comes from app.py's CUTS dict via a small
// JSON blob the template injects (window.CUT_DATA), so this file never
// has its own copy of filenames that can go stale.
const cutData = {};
Object.keys(window.CUT_DATA || {}).forEach(key => {
  const c = window.CUT_DATA[key];
  cutData[key] = {
    tag: c.tag,
    name: c.name,
    img: window.CUT_IMG_BASE + c.img,
    desc: c.desc,
  };
});

const cutTabs = document.querySelectorAll('.cut-tab');
const cutTag = document.getElementById('cutTag');
const cutName = document.getElementById('cutName');
const cutDesc = document.getElementById('cutDesc');
const cutPhoto = document.getElementById('cutPhoto');
const cutPhotoBg = document.getElementById('cutPhotoBg');

function selectCut(key, el){
  const d = cutData[key];
  if(!d) return;
  cutPhoto.style.opacity = 0;
  cutPhotoBg.style.opacity = 0;
  setTimeout(() => {
    cutTag.textContent = d.tag;
    cutName.textContent = d.name;
    cutDesc.textContent = d.desc;
    cutPhoto.src = d.img;
    cutPhoto.alt = d.name + ' — KSC Wholesale Chicken';
    cutPhotoBg.src = d.img;
    cutPhoto.style.opacity = 1;
    cutPhotoBg.style.opacity = 1;
  }, 150);
  cutTabs.forEach(t => t.classList.remove('active'));
  el.classList.add('active');
}

cutTabs.forEach(t => {
  t.addEventListener('click', () => selectCut(t.dataset.cut, t));
});

// Auto-dismiss flash messages
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => { el.style.transition = 'opacity .4s ease'; el.style.opacity = '0'; }, 5000);
});
