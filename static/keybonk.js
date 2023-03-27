
const keybonkModeChangeEvent = new Event('keybonkModeChange');

class Keybonk {
	updateWordSuggestions() {
		this.suggest.innerHTML = '';
		if(this.target==undefined || this.target==null || wordFreqDB==undefined || wordFreqDB==null)
			return;

		const start = this.target.selectionStart;
		const end = this.target.selectionEnd;
		if(start!=end)
			return;
			
		const word = this.target.value.slice(0, start).split(/\s+/).pop();
		if(word.length>0) {
			const kb = this;
			const lword = word.toLowerCase();
			const key = lword.substring(0, 6); // use MAX_KEY from proc_words.py
			const suggestions = wordFreqDB[key];
			if(suggestions!==undefined) {
				for(let i=0; i<suggestions.length; i++) {
					let key = document.createElement('div');
					key.classList.add('keybonk-suggest-item');
					const sug = suggestions[i];
					if(!sug.toLowerCase().startsWith(lword))
						continue;
						
					const sugEnd = sug.slice(word.length);
					key.innerHTML = word+sugEnd;
					
					key.addEventListener('click', function() {
						kb.typeCharacter(sugEnd+' ');
					});
					
					this.suggest.appendChild(key);
				}
			}
		}
	}
	
	switchTarget(e) {
		if(this.target!=undefined && this.target!=null)
			this.target.classList.remove('keybonk-target');
		this.target = e;
		this.target.classList.add('keybonk-target');
		if(this.target.value=='')
			if(this.onEmpty) this.onEmpty();
		this.updateWordSuggestions();
	}

	changeMode(mode) {
		if(this.keybonkMode!=mode) {
			this.keybonkMode = mode;
			for (const k of this.parentDiv.children) {
				k.dispatchEvent(keybonkModeChangeEvent);
			}
		}
	}
	
	onEmpty() {
		this.changeMode('shift');
	}
	
	onEnter() {
		kb.typeCharacter('\n');
	}

	trimSpace() {
		if(this.target==undefined || this.target==null)
			return;
		const start = this.target.selectionStart;
		const end = this.target.selectionEnd;
		if(typeof start == 'number' && typeof end == 'number' &&
				start==end && start>0 && this.target.value.charAt(start-1)==' ') {
			this.target.value = this.target.value.slice(0, start-1) + this.target.value.slice(end);
			this.target.selectionStart = start-1;
			this.target.selectionEnd = start-1;
		}
	}
	
	typeCharacter(ch) {
		if(this.target==undefined || this.target==null)
			return;
		this.target.focus();
		
		// Won't work in IE
		const start = this.target.selectionStart;
		const end = this.target.selectionEnd;
		if(typeof start == 'number' && typeof end == 'number') {
			this.target.value = this.target.value.slice(0, start) + ch + this.target.value.slice(end);
			this.target.selectionStart = start+ch.length;
			this.target.selectionEnd = start+ch.length;
			this.updateWordSuggestions();
		}
	}
	
	typeBackspace() {
		if(this.target==undefined || this.target==null)
			return;
		this.target.focus();
		
		// Won't work in IE
		var start = this.target.selectionStart;
		var end = this.target.selectionEnd;
		if((typeof start)=='number' && (typeof end)=='number') {
			if(end>start) {
				this.target.value = this.target.value.slice(0, start) + this.target.value.slice(end);
				this.target.selectionStart = start;
				this.target.selectionEnd = start;
				this.updateWordSuggestions();
			}
			else if(start>0) {
				this.target.value = this.target.value.slice(0, start-1) + this.target.value.slice(end);
				this.target.selectionStart = start-1;
				this.target.selectionEnd = start-1;
				this.updateWordSuggestions();
			}
		}
	}
	
	setKeyActive(key, active) {
		if(active)
			key.classList.add('keybonk-key-active');
		else
			key.classList.remove('keybonk-key-active');
	}
	
	constructor(parentDiv, target, keyWidth=50, keyMargin=2) {
		if(parentDiv==undefined)
			parentDiv = 'keybonk';
		if((typeof parentDiv)=='string')
			parentDiv = document.getElementById(parentDiv);
		this.parentDiv = parentDiv;
		
		if((typeof target)=='string')
			target = document.getElementById(target);
		this.target = target;
		
		const layout = ['qwertyuiop', 'asdfghjkl', '?zxcvbnm?', '?, .?'];
		const upLayout = ['QWERTYUIOP', 'ASDFGHJKL', '?ZXCVBNM?', '?? !?'];
		const numLayout = ['1234567890', '%$&*-+=()', '??!"\':;/?', '?, .?'];
		const symLayout = ['1234567890', '@#|\u00b0\u00f7\u00d7~[]', '?£\u20ac{}<>\\?', '?? !?'];
		const xoffs = [keyMargin, keyWidth/2+keyMargin, keyMargin, keyMargin];
		
		const kb = this;
		this.totalWidth = keyWidth*10 + keyMargin*20;
		
		kb.suggest = document.createElement('div');
		kb.suggest.classList.add('keybonk-suggest');
		parentDiv.appendChild(kb.suggest);
		
		for(let row=0; row<layout.length; row++) {
			for(let i=0; i<layout[row].length; i++) {
				let key = document.createElement('div');
				key.classList.add('keybonk-key');
				key.style.margin = keyMargin+'px';
				if(i==0)
					key.style.marginLeft = xoffs[row]+'px';
				
				if(row==2 && i==0) { // shift
					key.style.width = (keyWidth+keyWidth/2)+'px';
					
					key.addEventListener('keybonkModeChange', function() {
						if(kb.keybonkMode=='shift' || kb.keybonkMode=='default')
							key.innerHTML = '&#8679;';
						else
					key.innerHTML = '£#\\';
						kb.setKeyActive(key, kb.keybonkMode=='shift' || kb.keybonkMode=='sym');
					});
					
					key.addEventListener('click', function() {
						if(kb.keybonkMode=='shift')
							kb.changeMode('default');
						else if(kb.keybonkMode=='sym')
							kb.changeMode('num');
						else if(kb.keybonkMode=='num')
							kb.changeMode('sym');
						else
							kb.changeMode('shift');
					});
				}
				
				else if(row==2 && i==layout[row].length-1) { // backspace
					key.innerHTML = '&#129044;';
					key.style.width = (keyWidth+keyWidth/2)+'px';
					key.addEventListener('click', function() {
						kb.typeBackspace(target);
						if(kb.target.value=='')
							if(kb.onEmpty) kb.onEmpty();
					});
				}
				
				else if(row==3 && i==0) { // numeric
					key.style.width = (keyWidth+keyWidth/2)+'px';
					key.innerHTML = '123';
					
					key.addEventListener('keybonkModeChange', function() {
						kb.setKeyActive(key, kb.keybonkMode=='num' || kb.keybonkMode=='sym');
					});
					
					key.addEventListener('click', function() {
						if(kb.keybonkMode=='num' || kb.keybonkMode=='sym')
							kb.changeMode('default');
						else
							kb.changeMode('num');
					});
				}
				
				else if(row==3 && i==2) { // space
					key.style.width = (keyWidth*5+keyMargin*8)+'px';
					key.innerHTML = '&nbsp;';
					key.addEventListener('click', function() {
						kb.typeCharacter(' ');
					});
				}
				
				else if(row==3 && i==layout[row].length-1) { // enter
					key.innerHTML = '&#x21B2;';
					key.style.width = (keyWidth+keyWidth/2)+'px';
					key.addEventListener('click', function() {
						if(kb.onEnter) kb.onEnter();
					});
				}
				
				else {
					key.ch = layout[row].charAt(i);
					key.upch = upLayout[row].charAt(i);
					key.numch = numLayout[row].charAt(i);
					key.symch = symLayout[row].charAt(i);
					key.style.width = keyWidth+'px'

					key.addEventListener('keybonkModeChange', function() {
						if(kb.keybonkMode=='shift')
							key.innerHTML = this.upch;
						else if(kb.keybonkMode=='num')
							key.innerHTML = this.numch;
						else if(kb.keybonkMode=='sym')
							key.innerHTML = this.symch;
						else
							key.innerHTML = this.ch;
					});
					
					key.addEventListener('click', function() {
						let mode = kb.keybonkMode;
						let ch = this.ch;
						if(mode=='shift') {
							ch = this.upch;
							mode = 'default';
						}
						else if(mode=='num')
							ch = this.numch;
						else if(mode=='sym')
							ch = this.symch;

						if(ch==',' || ch=='.' || ch=='!' || ch=='?')
							kb.trimSpace();
						kb.typeCharacter(ch);
						
						if(mode!='num' && mode!='sym' && (ch=='.' || ch=='!' || ch=='?')) {
							kb.typeCharacter(' ');
							mode = 'shift';
						}
						
						kb.changeMode(mode);
					});
				}
				
				parentDiv.appendChild(key);
			}
			
			let br = document.createElement('div');
			br.style.cssFloat = 'none';
			br.style.clear = 'both';
			parentDiv.appendChild(br);
		}
		kb.changeMode('default');
	}
	
}

/*
window.addEventListener('DOMContentLoaded', function() {
	new Keybonk('keybonk');
}, false);
*/
