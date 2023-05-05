
// const mediaPath = 'https://storyweb.ams3.digitaloceanspaces.com';
// const mediaPath = 'https://storyweb.ams3.cdn.digitaloceanspaces.com';
const mediaPath = '../media';
// const mediaPath = 'http://localhost:8088/media';

const displayScale = 0.5;
const numDoors = 7;
const doorX = [45, 575, 1100, 1630];
const storyTimeout = 5000;

var allStories = presetStories; // TODO load stories, merge preset
//  Make sure the number of distinct objects in allStories >= numDoors

var storyQueue = [];
var doors;
var selectedStories;
var activeStory = -1;

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
	for(let i=0; i<numDoors; i++) {
		const s = popStoryQueue();
		if(isObjectSelected(s.obj)) {
			storyQueue.push(s);
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
	selectStories();
	var shuffle = [];
	for(let i=0; i<numDoors; i++)
		shuffle[i] = i;
	for(let i=0; i<numDoors; i++) {
		const door = doors[i];
		const row = shuffle.splice(Math.floor(Math.random() * shuffle.length), 1)[0];
		const pos = Math.floor(Math.random() * 4) + 4*row; // works only for numDoors = 7 and pos < 28
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

function init() {
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
	document.getElementById('content').style.display = 'block';
	
	openDoors();
	Yeet.start();
}
