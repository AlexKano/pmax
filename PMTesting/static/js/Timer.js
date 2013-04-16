var Timer = function() {};
jQuery.extend(Timer.prototype, {
	ID: null,
	TimerId: null,
	ElementToUpdate: null,
    IsTiming: false,
	_interval: 1000,
	
	Init: function(id, element) {
		this.ID = id;
		this.ElementToUpdate = element;
	},
	
	StartTimer: function(timersPool) {
		var self = this;
        self.IsTiming = true;
		self.TimerId = setInterval(function(){
            var oldText = self.ElementToUpdate.text().split(":");
            var seconds = +oldText[0] * 60 + +oldText[1];
            var newSecs = seconds + self._interval/1000;
            var m = Math.floor(newSecs / 60);
            var s = newSecs % 60;
            var newText = m + ":" + (s < 10 ? "0" : "") + s;
            self.ElementToUpdate.text(newText);
        }, self._interval);
		timersPool[self.ID].TimerId = self.TimerId;
	},
	
	StopTimer: function(timersPool) {
		clearInterval(timersPool[this.ID].TimerId);
        this.IsTiming = false;
	}
	
//	_updateTimer: function(self) {
//        var oldText = self.ElementToUpdate.text().split(":");
//        var seconds = oldText[0] * 60 + oldText[1];
//        var newSecs = seconds + self._interval/1000;
//        var newText = self._timeFormat.format(Math.floor(newSecs / 60), newSecs % 60);
//		this.ElementToUpdate.text(newText);
//	}
});

var TimersPool = function() {};
jQuery.extend(TimersPool.prototype, {
	Pool: [],
	
	Init: function(deviceFormIdClass) {
		var count = $(deviceFormIdClass).length;
		this.Pool = new Array(count);
	}
});