
const mediaProxyPath = 'http://localhost:8088/media';
var mediaPath = 'https://storyweb.ams3.cdn.digitaloceanspaces.com';

const timeoutLimit = 60;

var objectIds = [];

var selectedSlot;
var selectedData;
var uiPage = null;
var uiReturnPage = null;
var pageId;
var objectUIReady = false;
var objectVideoReady = false;

var keybonk;
var wordFreqDB = null;
var countdown, timeout, timeoutTimer;

function switchKBTarget(e) {
	if(keybonk!==undefined)
		keybonk.switchTarget(e);
}

function onUserInput() {
	if(keybonk!==undefined) {
		const len = keybonk.target.value.length;
		document.getElementById('char-count-'+keybonk.target.id).innerHTML = `${len}&nbsp;/&nbsp;100`;
		keybonk.updateWordSuggestions();
	}
}

function turnLever(e, dt, t) {
	const turn = document.getElementById('lever-turn');
	e.yeet.a = turn.drag.angle;
}

function rerollOptions() {
	const oldIds = objectIds;
	objectIds = [];
	for(i=0; i<3; i++) {
		for(;;) {
			let opt = allOptions[Math.floor(Math.random() * allOptions.length)];
			if(!objectIds.includes(opt) && !oldIds.includes(opt)) {
				objectIds.push(opt);
				break;
			}
		}
	}
}

function pullLever() {
	if(window.loadedData) {
		window.allData = window.loadedData;
		window.allOptions = Object.keys(window.allData);
		window.loadedData = undefined;
	}
	document.getElementById('click-block').style.display = 'block';
	document.getElementById('cab-labels').style.display = 'none';
	
	for(let i=0; i<3; i++) {
		const doorBox = document.getElementById('door'+i);
		const doorImg = document.getElementById('door-img'+i);
		Yeet.tween(doorImg, {'sy':1}, {'duration':0.1, 'easing':Yeet.easingOut, 'p':5, 'onfinish': function() {
			doorBox.style.display = 'none';
		}});
	}
	
	let ready = 0;
	const lever = document.getElementById('lever');
	Yeet.tween(lever, {'a':45}, {'duration': 0.4, 'easing':Yeet.easeOut, 'p':2, 'onfinish': function() {
		rerollOptions();
		for(let i=0; i<3; i++) {
			const doorObj = document.getElementById('door-obj'+i);
			doorObj.src = `${mediaPath}/${objectIds[i]}.jpg`;
			
			const cab = document.getElementById('cab'+i);
			const doorBox = document.getElementById('door'+i);
			const doorImg = document.getElementById('door-img'+i);
			doorImg.yeet.sy = 1;
			
			let nextIndex = 0;
			let nexty = cab.yeet.y;
			while(Math.abs(nexty - cab.yeet.y)<=700) {
				nextIndex = Math.floor(Math.random()*6); // 9
				nexty = -350 * nextIndex;
			}
			
			Yeet.tween(cab, {'y':nexty}, {
				'duration': 1.0+Math.random()*1.2,
				'easing': Yeet.easeInOut, 'p':3,
				'onfinish': function() {
					ready++;
					if(ready==3) {
						document.getElementById('click-block').style.display = 'none';
						document.getElementById('cab-labels').style.display = 'block';
						/*setTimeout(function() {
							Yeet.stop();
						}, 300);*/
					}
					
					const bgy = -30-((nextIndex+1)%9)*350;
					doorImg.style.backgroundPosition = `-30px ${bgy}px`;
					doorBox.style.display = 'block';
					Yeet.tween(doorImg, {'sy':0}, {'duration':0.25, 'easing':Yeet.easeOut, 'p':3});
				}
			});
		}
		setTimeout(function() {
			Yeet.tween(lever, {'a':-45}, {'duration': 1, 'easing':Yeet.easeOut, 'p':1.5, 'onfinish': function() {
				lever.yeet.func = turnLever;
			}});
		}, 250);
	}});
	
	Yeet.start();
}

function startVideo() {
	if(!objectUIReady || !objectVideoReady)
		return;
	const video = document.getElementById('object-video');
	video.pause();
	video.currentTime = 0;
	video.muted = true;
	video.play();
}

function videoLoaded() {
	objectVideoReady = true;
	startVideo();
}

function openObject(slot) {
	const objectId = objectIds[slot];
	if(!(objectId in allData))
		return;
	selectedSlot = slot;
	selectedData = allData[objectId];
	
	document.getElementById('object-main').style.display = 'block';
	document.getElementById('lever-click').style.display = 'none';
	document.getElementById('cab-labels').style.display = 'none';

	const wallLeft = document.getElementById('wall-left');
	wallLeft.style.display = 'block';
	wallLeft.yeet.sx = 0.315;
	wallLeft.yeet.sy = 0.315;
	wallLeft.yeet.x = 35 + 400*slot;
	wallLeft.yeet.y = 370;
	Yeet.tween(wallLeft, {'x':0,'y':0,'sx':1,'sy':1}, {'duration':0.4, 'easing':Yeet.easeIn, 'p':5});
	
	const wallRight = document.getElementById('wall-right');
	wallRight.style.display = 'block';
	wallRight.yeet.sx = 0.315;
	wallRight.yeet.sy = 0.315;
	wallRight.yeet.x = 35 + 340 - 60*0.315 + 400*slot;
	wallRight.yeet.y = 370;
	Yeet.tween(wallRight, {'x':1140,'y':0,'sx':1,'sy':1}, {'duration':0.4, 'easing':Yeet.easeIn, 'p':5});
	
	const video = document.getElementById('object-video');
	video.style.display = 'none';
	objectUIReady = false;
	
	const cover = document.getElementById('object-cover');
	cover.src = `${mediaPath}/${objectId}.jpg`;
	cover.yeet.sx = 0.315;
	cover.yeet.sy = 0.315;
	cover.yeet.x = 35 + 400*slot;
	cover.yeet.y = 370;
	Yeet.tween(cover, {'x':60,'y':0,'sx':1,'sy':1}, {'duration':0.4, 'easing':Yeet.easeIn, 'p':5, 'onfinish': function() {
		objectUIReady = true;
		
		video.src = `${mediaPath}/${objectId}.webm`;
		video.poster = `${mediaPath}/${objectId}.jpg`;
		objectVideoReady = false;
		video.style.display = 'block';
		startVideo();
		
		uiPage = document.getElementById('ui-page-open');
		uiPage.style.display = 'block';
		document.getElementById('open-name').innerHTML = selectedData['name'];
		document.getElementById('open-fact').innerHTML = selectedData['fact'];
		
		Yeet.stop();
		countdown = document.getElementById('countdown-open');
		startCountdown();
	}});
	
	Yeet.start();
}

function closeObject() {
	document.getElementById('q1').value = '';
	document.getElementById('q2').value = '';
	document.getElementById('q3').value = '';
	
	document.getElementById('object-main').style.display = 'block';
	document.getElementById('keybonk').style.display = 'none';
	if(uiPage) {
		uiPage.style.display = 'none';
		uiPage = null;
	}
	pageId = undefined;
	countdown = null;
	objectUIReady = false;
	
	const wallLeft = document.getElementById('wall-left');
	Yeet.tween(wallLeft, {
			'sx': 0.315, 'sy': 0.315,
			'x': 35 + 400*selectedSlot,
			'y': 370
		}, {'duration':0.4, 'easing':Yeet.easeOut, 'p':5});
	const wallRight = document.getElementById('wall-right');
	Yeet.tween(wallRight, {
			'sx': 0.315, 'sy': 0.315,
			'x': 35 + 340 - 60*0.315 + 400*selectedSlot,
			'y': 370
		}, {'duration':0.4, 'easing':Yeet.easeOut, 'p':5});
	
	const video = document.getElementById('object-video');
	video.pause();
	video.style.display = 'none';
	
	const cover = document.getElementById('object-cover');
	Yeet.tween(cover, {
			'sx': 0.315, 'sy': 0.315,
			'x': 35 + 400*selectedSlot,
			'y': 370
		}, {'duration':0.4, 'easing':Yeet.easeOut, 'p':5, 'onfinish': function() {
			wallLeft.style.display = 'none';
			wallRight.style.display = 'none';
			document.getElementById('object-main').style.display = 'none';
			document.getElementById('lever-click').style.display = 'block';
			document.getElementById('cab-labels').style.display = 'block';
			
			Yeet.stop();
		}});
		
	Yeet.start();
}

function sanitize(s) {
    return s.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
}

function insertAnswer(id) {
	const text = sanitize(document.getElementById(id).value.trim());
	if(!text) {
		document.getElementById('ins-'+id).innerHTML = '&nbsp;...&nbsp;';
		return false;
	}
	else {
		document.getElementById('ins-'+id).innerHTML = text;
		return true;
	}
}

function flipPage(id) {
	if(uiPage)
		uiPage.style.display = 'none';
	pageId = id;
	if(typeof id === 'string' || id instanceof String)
		uiPage = document.getElementById('ui-page-'+id);
	else
		uiPage = id;
	uiPage.style.display = 'block';
	
	if(id=='q1' || id=='q2' || id=='q3') {
		document.getElementById('keybonk').style.display = 'block';
		document.getElementById(id).focus();
	}
	else
		document.getElementById('keybonk').style.display = 'none';
		
	if(id=='done') {
		const insName = document.getElementById('story-title');
		if(insName) insName.innerHTML = selectedData['name'];
		const insFact = document.getElementById('story-fact');
		if(insFact) insFact.innerHTML = selectedData['fact'];
		
		let sharePrompt = 'Share it so that others might be inspired<br/>or go back and change it?';
		let canSend = insertAnswer('q1') & insertAnswer('q2') & insertAnswer('q3');
		if(!canSend)
			sharePrompt = 'Please answer all questions to continue.';
		const storyText = document.getElementById('story-content-wrap');
		if(storyText.scrollWidth > 558 || storyText.scrollHeight > 540) {
			canSend = false;
			console.log(`storyText size: ${storyText.scrollWidth} x ${storyText.scrollHeight}`);
			sharePrompt = 'Oops! Your story is too long.<br/>Please shorten it a bit.';
		}
		document.getElementById('btnshare').disabled = !canSend;
		document.getElementById('share-prompt').innerHTML = sharePrompt;
	}
	else if(id=='send') {
		postStory();
	}
	
	countdown = document.getElementById('countdown-'+id);
	startCountdown();
}

function modalPage(id) {
	uiReturnPage = uiPage;
	flipPage(id);
}

function modalReturn() {
	if(uiReturnPage) {
		flipPage(uiReturnPage);
		uiReturnPage = null;
	}
	else
		closeObject();
}

function confirmCloseObject() {
	modalPage('confirm-close');
}

function postStory() {
	const objectId = objectIds[selectedSlot];
	const q1 = encodeURIComponent(document.getElementById('q1').value.trim());
	const q2 = encodeURIComponent(document.getElementById('q2').value.trim());
	const q3 = encodeURIComponent(document.getElementById('q3').value.trim());
	
	const abortc = new AbortController();
	setTimeout(() => abortc.abort(), 3000)
	const url = `/post?obj=${objectId}&q1=${q1}&q2=${q2}&q3=${q3}`;
	fetch(url, { signal: abortc.signal }).then(resp => resp.json()).then(d => {
		document.getElementById('storylink').href = d['story'];
		document.getElementById('qrcode').src = d['qr'];
		flipPage('qr');
	}).catch(e => {
		flipPage('send-err');
	});
}

function startCountdown() {
    window.onmousedown = resetTimer;
    window.ontouchstart = resetTimer;
    window.ontouchmove = resetTimer;
    window.onclick = resetTimer;
    window.onkeydown = resetTimer;   
	
	function updateCountdown() {
		if(countdown!==null && countdown!==undefined) {
			if(timeout>0) {
				timeout = timeout - 1;
				if(timeout<=30) {
					countdown.innerHTML = timeout;
					countdown.style.display = 'inline-block';
				}
				else
					countdown.style.display = 'none';
				continueTimer();
			}
			else {
				closeObject();
			}
		}
	}
	function continueTimer() {
		timeoutTimer = setTimeout(updateCountdown, 1000);
	}
	function resetTimer() {
		clearTimeout(timeoutTimer);
		if(countdown!==null && countdown!==undefined) {
			timeout = timeoutLimit;
			countdown.style.display = 'none';
			continueTimer();
		}
	}
	resetTimer();
}

function loadData() {
	fetch('object_data.json', {cache: "no-store"}).then(resp => resp.json()).then(d => {
		window.loadedData = d;
		const content = document.getElementById('content');
		if(content.style.display!='block') {
			content.style.display = 'block';
			pullLever();
		}
		setTimeout(loadData, 3600000); // 1 hour
	});
}

function parseHashParams() {
	let hash = location.hash;
	if(hash.length==0)
		return;
	hash = hash.replace('#','');
	const params = hash.split(',');
	for(let i=0; i<params.length; i++) {
		const param = params[i];
		if(param=='mproxy') {
			mediaPath = mediaProxyPath;
			console.log('Using media proxy at '+mediaProxyPath);
		}
		else {
			console.warn('Unknown hash parameter '+param);
		}
	}
}

function init() {
	parseHashParams();
	
	const pix = window.devicePixelRatio;
	if(pix!=1) {
		document.body.style.transform = `scale(${1/pix})`;
		document.body.style.width = `${pix*100}%`;
		document.body.style.height = `${pix*100}%`;
	}
	
	keybonk = new Keybonk('keybonk', undefined, 62);
	keybonk.onEmpty = null;
	keybonk.onEnter = function() {
		if(pageId) {
			const btnNext = document.getElementById('btnnext-'+pageId);
			btnNext.click();
		}
	};
	fetch('words.json').then(resp => resp.json()).then(data => { wordFreqDB = data; });
	document.addEventListener('selectionchange', onUserInput);

	Yeet.initElements();
	
	if(typeof staticData==='undefined' || !staticData) {
		loadData();
	}
	else {
		document.getElementById('content').style.display = 'block';
		pullLever();
	}
	
	const parentR = 540;
	const handleR = 550;
	const R = 460;
	const a0 = -Math.PI/4; // -45
	const a1 = a0 + Math.PI/6; // -45+30
	const turn = document.getElementById('lever-turn');
	function resetLeverTurn() {
		turn.style.left = Math.round(R*Math.cos(a0) + (parentR-handleR))+'px';
		turn.style.top = Math.round(R*Math.sin(a0) + (parentR-handleR))+'px';
	}
	resetLeverTurn();
	
	new Drag(turn, turn, function(drag, pos) {
		const dx = pos.x - (parentR-handleR);
		const dy = pos.y - (parentR-handleR);
		let a = Math.atan2(dy, dx);
		if(a<a0) a = a0;
		let stop = false;
		if(a>a1) {
			a = a0;
			stop = true;
		}
		drag.angle = a*180/Math.PI;
		pos.x = R*Math.cos(a) + (parentR-handleR);
		pos.y = R*Math.sin(a) + (parentR-handleR);
		if(stop) drag.stop();
	}).onStopDrag = function() {
		turn.drag.angle = -45;
		resetLeverTurn();
		pullLever();
	}
}
