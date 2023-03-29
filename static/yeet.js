
class Yeet {
	static #startTime;
	static #prevTime;
	static #animReq;
	static #list;
	
	static initElement(e, data) {
		const yeet = {};
		yeet.x = Math.floor(e.offsetLeft);
		yeet.y = Math.floor(e.offsetTop);
		yeet.a = 0;
		yeet.sx = 1;
		yeet.sy = 1;
		if(data) {
			if(typeof data === 'string' || data instanceof String)
				data = JSON.parse(data.replaceAll('\'', '"'));
			for(const p in data) {
				if(p=='func')
					yeet.func = window[data['func']];
				else
					yeet[p] = data[p];
			}
		}
		e.yeet = yeet;
		if(e.yeet.func && e.yeet.func instanceof Function)
			e.yeet.func(e, 0, 0);
		else
			Yeet.defaultFunc(e, 0, 0);
		Yeet.apply(e);
	}
	
	static initElements(force=false) {
		Yeet.#list = document.getElementsByClassName('yeet');
		for(let i=0; i<Yeet.#list.length; i++) {
			const e = Yeet.#list.item(i);
			if(force || !e.hasOwnProperty('yeet'))
				Yeet.initElement(e, e.dataset.yeet);
		}
	}
	
	static apply(e) {
		e.style.left = Math.round(e.yeet.x)+'px';
		e.style.top = Math.round(e.yeet.y)+'px';
		e.style.transform = `rotate(${e.yeet.a}deg) scale(${e.yeet.sx}, ${e.yeet.sy})`;
	}

	static defaultFunc(e, dt, t) {
		const yeet = e.yeet;
		if(yeet.dx) yeet.x += dt*yeet.dx;
		if(yeet.dy) yeet.y += dt*yeet.dy;
		if(yeet.da) yeet.a += dt*yeet.da;
	}
	
	static #onAnimate(time) {
		if(Yeet.#startTime===undefined) {
			Yeet.#startTime = time;
			Yeet.#prevTime = time;
		}
		const t = (time-Yeet.#startTime)/1000;
		const dt = (time-Yeet.#prevTime)/1000;
		Yeet.#prevTime = time;
		
		for(let i=0; i<Yeet.#list.length; i++) {
			const e = Yeet.#list.item(i);
			if(e.yeet.func instanceof Function)
				e.yeet.func(e, dt, t);
			else
				Yeet.defaultFunc(e, dt, t);
			Yeet.apply(e);
		}
		Yeet.#animReq = requestAnimationFrame(Yeet.#onAnimate);
	}
	
	static start() {
		Yeet.#animReq = requestAnimationFrame(Yeet.#onAnimate);
	}
	
	static stop() {
		cancelAnimationFrame(Yeet.#animReq);
	}
	
	static lerp(x0, x1, s) {
		return x0*(1-s) + x1*s;
	}

	static tween(e, values, params) {
		const vals = {};
		for(const [name, value] of Object.entries(values))
			vals[name] = [e.yeet[name], value];
			
		const tween = { 's': 0 };
		
		e.yeet.func = function(e, dt, t) {
			tween.s += dt / params.duration;
			if(tween.s>=1) {
				e.yeet.func = null;
				for(const [name, value] of Object.entries(vals))
					e.yeet[name] = value[1];
				if(params.onfinish instanceof Function)
					params.onfinish(e);
			}
			else {
				const s = (params.easing instanceof Function) ?
						params.easing(tween.s, params.p) : tween.s;
				for(const [name, value] of Object.entries(vals))
					e.yeet[name] = Yeet.lerp(value[0], value[1], s);
			}
		}
	}
	
	static easeOut(s, p) {
		if(!p) p = 2;
		return Math.pow(s, p);
	}
	
	static easeIn(s, p) {
		if(!p) p = 2;
		return 1 - Math.pow(1-s, p);
	}

	static easeInOut(s, p) {
		return s<0.5 ?
			0.5-0.5*Yeet.easeIn(1-s*2, p) :
			0.5+0.5*Yeet.easeIn(s*2-1, p);
	}
	
	static easeSin(s, p) {
		if(!p) p = 0;
		s = s*(1+2*p)-p;
		return (Math.sin(s*Math.PI-Math.PI/2) / Math.sin(Math.PI/2-p*Math.PI))*0.5+0.5;
	}
}
