
// Derived from https://www.w3schools.com/howto/howto_js_draggable.asp

class Drag {
	elem;
	limitFunc;
	prevx = 0;
	prevy = 0;
	startx = 0;
	starty = 0;
	posx = 0;
	posy = 0;
	enabled = true;
	
	constructor(elem, dragElem=null, limitFunc=undefined) {
		const drag = this;
		elem.drag = this;
		this.elem = elem;
		this.limitFunc = limitFunc;
		if(dragElem!==null && dragElem!==undefined)
			dragElem.onpointerdown = dragMouseDown;
		else
			elem.onpointerdown = dragMouseDown;
			
		function dragMouseDown(e) {
			if(!drag.enabled)
				return;
			e = e || window.event;
			e.preventDefault();
			drag.prevx = e.clientX;
			drag.prevy = e.clientY;
			drag.startx = drag.x;
			drag.starty = drag.y;
			drag.posx = drag.elem.offsetLeft;
			drag.posy = drag.elem.offsetTop;
			document.onpointerup = dragMouseUp;
			document.onpointermove = dragMouseMove;
			
			if(drag.onStartDrag instanceof Function)
				drag.onStartDrag(drag.elem, drag.posx, drag.posy);
		}

		function dragMouseMove(e) {
			e = e || window.event;
			e.preventDefault();
			const dx = drag.prevx - e.clientX;
			const dy = drag.prevy - e.clientY;
			drag.prevx = e.clientX;
			drag.prevy = e.clientY;
			
			let pos = {
				'x': drag.elem.offsetLeft - dx,
				'y': drag.elem.offsetTop - dy
			};
			if(limitFunc instanceof Function)
				limitFunc(drag, pos);

			drag.posx = pos.x;
			drag.posy = pos.y;
			drag.elem.style.top = pos.y + "px";
			drag.elem.style.left = pos.x + "px";

			if(drag.onDrag instanceof Function)
				drag.onDrag(drag.elem, pos.x, pos.y);
		}

		function dragMouseUp() {
			drag.stop();
		}
	}

	stop(call=true) {
		document.onpointerup = null;
		document.onpointermove = null;
		if(call && this.onStopDrag instanceof Function)
			this.onStopDrag(this.elem, this.posx, this.posy);
	}
	
	static limitRect(drag, pos, rect) {
		if(pos.x<rect.left) pos.x = rect.left;
		if(pos.x>rect.right) pos.x = rect.right;
		if(pos.y<rect.top) pos.y = rect.top;
		if(pos.y>rect.bottom) pos.y = rect.bottom;
	}
}
