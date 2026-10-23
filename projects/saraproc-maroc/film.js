// All animation belongs to a paused, seekable root timeline.
window.__timelines = window.__timelines || {};
const film = gsap.timeline({paused:true});
const scenes = [...document.querySelectorAll('.scene')];
for (let index=0; index<scenes.length; index++) {
  const scene=scenes[index];
  const start=Number(scene.dataset.t0);
  const end=Number(scene.dataset.t1);
  const bridge=scene.classList.contains('chapter-bridge');
  const duration=end-start;
  if(index>0) {
    // A crossfade is the scene transition; content holds until this begins.
    const crossfade=bridge?0.5:0.6;
    film.to(scenes[index-1],{opacity:0,duration:crossfade,ease:'sine.inOut'},start);
    film.to(scene,{opacity:1,duration:crossfade,ease:'sine.inOut'},start);
  }
  const units=[...scene.querySelectorAll('.reveal')];
  units.forEach((unit,i)=>{
    const t=start+0.18+i*(bridge?0.1:0.12);
    if(unit.classList.contains('logo') || unit.classList.contains('brand-panel')) {
      film.from(unit,{opacity:0,scale:0.96,duration:bridge?0.48:0.85,ease:'sine.out'},t);
    } else if(unit.classList.contains('kicker')) {
      film.from(unit,{opacity:0,x:-22,duration:0.6,ease:'power2.out'},t);
    } else if(unit.classList.contains('visual')) {
      if(index===0) {
        // The opening thumbnail already contains the hero image.
        film.from(unit,{scale:1.025,duration:1.2,ease:'sine.out'},0);
      } else {
        film.from(unit,{opacity:0,x:32,duration:0.95,ease:'power3.out'},t);
      }
    } else if(unit.classList.contains('rule')) {
      film.from(unit,{scaleX:0,transformOrigin:'left center',duration:0.65,ease:'expo.out'},t);
    } else {
      film.from(unit,{opacity:0,y:24,duration:0.7,ease:i%2?'power3.out':'expo.out'},t);
    }
  });
  scene.querySelectorAll('.drift').forEach((photo,i)=>{
    film.to(photo,{scale:1.04,duration:Math.max(1,duration-.5),ease:'sine.inOut'},start+.1);
  });
  const ambient=scene.querySelector('.ambient');
  if(ambient) film.to(ambient,{x:-80,y:50,duration:duration,ease:'sine.inOut'},start);
}
window.__timelines.main=film;
