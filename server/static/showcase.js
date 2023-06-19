
const mediaProxyPath = 'http://localhost:8088/media';
var mediaPath = 'https://storyweb.ams3.cdn.digitaloceanspaces.com';

var displayScale = 1;
const numDoors = 7;
const doorX = [45, 575, 1100, 1630];
const storyTimeout = 20000;

var allStories = presetStories;

var storyQueue = [];
var doors;
var selectedStories;
var activeStory = -1;

function checkLoadedStories(stories) {
	stories = stories.filter(s => window.allOptions.has(s.obj));

	let distinctObjects = stories.length;
	if(distinctObjects>=numDoors) {
		const objects = new Set();
		distinctObjects = 0;
		for(let i=0; distinctObjects<numDoors && i<stories.length; i++) {
			const obj = stories[i].obj;
			if(!objects.has(obj)) {
				objects.add(obj);
				distinctObjects++;
			}
		}
	}
	console.log(`Loaded ${stories.length} stories`);
	if(distinctObjects<numDoors) {
		console.warn(`${distinctObjects} distinct objects. Merging with preset stories.`);
		return stories.concat(presetStories);
	}
	else
		return stories;
}

function popStoryQueue() {
	if(storyQueue.length==0) {
		let shuffle = [...allStories];
		while(shuffle.length>0) {
			const s = shuffle.splice(Math.floor(Math.random() * shuffle.length), 1)[0];
			storyQueue.push(s);
		}
	}
	return storyQueue.shift();
}

function isObjectSelected(obj) {
	for(let i=0; i<selectedStories.length; i++) {
		if(selectedStories[i].obj==obj)
			return true;
	}
	return false;
}

function selectStories() {
	selectedStories = [];
	let redo = 0;
	const maxRedo = allStories.length;
	for(let i=0; i<numDoors; i++) {
		const s = popStoryQueue();
		if(redo<maxRedo && isObjectSelected(s.obj)) {
			if(redo<storyQueue.length)
				storyQueue.push(s);
			redo++;
			i--;
		}
		else {
			selectedStories.push(s);
		}
	}
}

function placeDoor(door, pos) {
	door.style.display = 'block';
	const posx = doorX[pos%4];
	const posy = 3840 - (45+457)*(Math.floor(pos/4)+1);
	door.pos = pos;
	door.posx = posx;
	door.posy = posy;
	door.style.left = `${posx}px`;
	door.style.top = `${posy}px`;
	door.doorImg.style.backgroundPosition = `-${posx}px -${posy}px`;
}

function openDoors() {
	if(window.loadedData) {
		window.allData = window.loadedData;
		window.allOptions = new Set(Object.keys(window.allData));
		window.loadedData = undefined;
	}
	if(window.loadedStories) {
		window.allStories = checkLoadedStories(window.loadedStories);
		window.loadedStories = undefined;
		storyQueue = [];
	}
	
	selectStories();
	var shuffle = [];
	for(let i=0; i<numDoors; i++)
		shuffle[i] = i;
	let prevPosX = -1;
	for(let i=0; i<numDoors; i++) {
		const door = doors[i];
		const row = shuffle.splice(Math.floor(Math.random() * shuffle.length), 1)[0];
		
		let posx = -1;
		while(posx<0 || posx==prevPosX)
			posx = Math.floor(Math.random() * 4);
		prevPosX = posx;
		
		const pos = posx + 4*row; // works only for numDoors = 7 and pos < 28
		placeDoor(door, pos);
		door.doorObj.src = `${mediaPath}/${selectedStories[i].obj}.jpg`;
		door.doorImg.style.display = 'block';
		Yeet.tween(door.doorImg, {'sy':0}, {'duration':0.2+0.2*Math.random(), 'easing':Yeet.easeOut, 'p':3});
	}
	
	activeStory = -1;
	setTimeout(openStory, 500);
}

function closeDoors() {
	for(let i=0; i<numDoors; i++) {
		const door = doors[i];
		Yeet.tween(door.doorImg, {'sy':1}, {'duration':0.2+0.2*Math.random(), 'easing':Yeet.easeIn, 'p':3});
	}
	setTimeout(openDoors, 1000);
}

function sanitize(s) {
    return s.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
}

function openStory() {
	activeStory++;
	if(activeStory>=numDoors) {
		closeDoors()
		return;
	}
	const door = doors[activeStory];
	const story = selectedStories[activeStory];
	const objectId = story.obj;
	
	const objFrame = document.getElementById('object-frame');
	objFrame.style.display = 'block';
	objFrame.yeet.sx = 0.45;
	objFrame.yeet.sy = 0.45;
	objFrame.yeet.x = door.posx-23;
	objFrame.yeet.y = door.posy-37;
	Yeet.tween(objFrame, {'x':490,'y':490,'sx':1,'sy':1}, {'duration':0.75, 'easing':Yeet.easeIn, 'p':3});
	
	const objCover = document.getElementById('object-cover');
	objCover.src = `${mediaPath}/${objectId}.jpg`;
	objCover.style.display = 'block';
	objCover.yeet.sx = 0.45;
	objCover.yeet.sy = 0.45;
	objCover.yeet.x = door.posx;
	objCover.yeet.y = door.posy-14;
	Yeet.tween(objCover, {'x':540,'y':540,'sx':1,'sy':1}, {'duration':0.75, 'easing':Yeet.easeIn, 'p':3});
	
	setTimeout(function() {
		document.getElementById('story-title').innerHTML = allData[objectId].name;
		document.getElementById('story-fact').innerHTML = allData[objectId].fact;
		document.getElementById('ins-q1').innerHTML = sanitize(story.q1);
		document.getElementById('ins-q2').innerHTML = sanitize(story.q2);
		document.getElementById('ins-q3').innerHTML = sanitize(story.q3);
		
		const storyBox = document.getElementById('story-box');
		storyBox.style.display = 'block';
		storyBox.yeet.x = -1100;
		Yeet.tween(storyBox, {'x':540}, {'duration':0.75, 'easing':Yeet.easeIn, 'p':3, 'onfinish': function() {
			document.getElementById('object-video').src = `${mediaPath}/${objectId}.webm`;
		}});
		
		setTimeout(closeStory, storyTimeout);
	}, 750);
}

function closeStory() {
	const storyBox = document.getElementById('story-box');
	storyBox.style.display = 'block';
	Yeet.tween(storyBox, {'x':2260}, {'duration':0.75, 'easing':Yeet.easeOut, 'p':3, 'onfinish': function() {
			document.getElementById('object-video').style.display = 'none';
			storyBox.style.display = 'none';
			const door = doors[activeStory];
			
			const objFrame = document.getElementById('object-frame');
			Yeet.tween(objFrame, {
					'sx': 0.45, 'sy': 0.45,
					'x': door.posx-23,
					'y': door.posy-37
				}, {'duration':0.75, 'easing':Yeet.easeOut, 'p':3});
			
			const objCover = document.getElementById('object-cover');
			Yeet.tween(objCover, {
					'sx': 0.45, 'sy': 0.45,
					'x': door.posx,
					'y': door.posy-14
				}, {'duration':0.75, 'easing':Yeet.easeOut, 'p':3, 'onfinish': function() {
					objFrame.style.display = 'none';
					objCover.style.display = 'none';
					setTimeout(openStory, 500);
				}});
		}});
}

function videoLoaded() {
	const video = document.getElementById('object-video');
	video.style.display = 'block';
	video.pause();
	video.currentTime = 0;
	video.muted = true;
	video.play();
}

function makeDoor(layer, index) {
	const door = document.createElement('div');
	door.id = 'door'+index;
	door.classList.add('door-box');
	layer.appendChild(door);
	door.innerHTML = `<img id="door-obj${index}" class="door-obj" draggable="false" onclick="openObject(${index})" />
		<div id="door-img${index}" class="yeet door-img" data-yeet="{'x':0,'y':0}"></div>`;
	door.doorImg = document.getElementById('door-img'+index);
	door.doorObj = document.getElementById('door-obj'+index);
	return door;
}

function dataReady() {
	if(window.waitData)
		window.waitData--;
	if(window.waitData)
		return;
	
	const content = document.getElementById('content');
	if(content.style.display!='block') {
		content.style.display = 'block';
		openDoors();
		Yeet.start();
	}
}

function loadData() {
	fetch('object_data.json', {cache: "no-store"}).then(resp => resp.json()).then(d => {
		window.loadedData = d;
		dataReady();
	});
	setTimeout(loadData, 1800000); // 30 min
}

function loadStories() {
	fetch('/showcase', {cache: "no-store"}).then(resp => resp.json()).then(d => {
		window.loadedStories = d;
		dataReady();
	});
	setTimeout(loadStories, 300000); // 5 min
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
		else if(param.startsWith('s=')) {
			displayScale = parseFloat(param.substring(2));
			console.log('Using display scale of '+displayScale);
		}
		else {
			console.warn('Unknown hash parameter '+param);
		}
	}
}

function init() {
	parseHashParams();
	
	const pix = window.devicePixelRatio;
	if(pix!=1 || displayScale!=1) {
		document.body.style.transform = `scale(${displayScale/pix})`;
		document.body.style.width = `${pix*100/displayScale}%`;
		document.body.style.height = `${pix*100/displayScale}%`;
	}

	const doorLayer = document.getElementById('door-layer');
	doors = [];
	for(let i=0; i<numDoors; i++) {
		doors.push(makeDoor(doorLayer, i));
	}

	Yeet.initElements();
	
	if(typeof staticData==='undefined' || !staticData) {
		window.waitData = 2;
		loadData();
		loadStories();
	}
	else {
		document.getElementById('content').style.display = 'block';
		openDoors();
		Yeet.start();
	}
}
