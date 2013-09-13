function Updater() { }
Updater.prototype = {
	settings: {
		Url: null,
		Interv: 1000,
		Handler: null,
		//Context: null
	},
	
	_updaterId: null,
	_isUpdating: false,
	_errorBlock: null,
	
	Init: function(options){
		$.extend(this.settings, options);
		this._initErrorBlock();
	},
	
	_initErrorBlock: function() {
		var css = {
			'background': '#666', 
			"color": "#fff", 
			"position": "absolute", 
			"left": "10px", 
			"right": "10px"
		};
		this._errorBlock = $('<div id="errorBlock"></div>').css(css);
		this._errorBlock.hide().appendTo( $("body") );
	},
	
	StartUpdater: function(){
		var self = this;
		if (self._isUpdating) return;

		var settings = self.settings;
		settings._updaterId = setInterval(function() {
			document.DEBUG && console.log(settings.Url);
			$.ajax({
				type: "GET",
				cache : false,
				url: settings.Url,
				success: function(json) {					
					var data = $.parseJSON(json);
					document.DEBUG && console.log(json, data);
					
					data.error ? self.ShowError(data.error) : settings.Handler(data);
				}
			});
		}, settings.Interv);
		self._isUpdating = true;
	},
	
	ShowError: function(message) {
		this._errorBlock
			.innerHTML(message).show()
			.setTimeout(function () {
				self._errorBlock.hide(250);
			}, 750);
	},
	
	StopUpdater: function() {
		if (this._isUpdating){
			clearInterval(this.settings._updaterId);
			this._isUpdating = !this._isUpdating;
		}
    }
}

// base class
function Form() {}
Form.prototype = {	
	_updaters: [],
	
	StartUpdater: function(url, func, interv){
		var settings = this._getUpdaterSettings(url, func, interv);
		
		var newUpdater = new Updater();
		newUpdater.Init(settings);
		newUpdater.StartUpdater();
		
		this._updaters.push(newUpdater);
		var updaterIndex = this._updaters.length - 1;
		return updaterIndex;
	},
	
	StopUpdater: function(index){
		this._updaters[index].StopUpdater();
		delete this._updaters[index];
	},
	
	_getUpdaterSettings: function(url, func, interv){
		return {
			Url: url,
			Interv: interv,
			Handler: func,
			//Context: this,
		};
	},

    Submit: function(form, evt){
        evt.preventDefault();
        var btn = evt.originalEvent.explicitOriginalTarget;

        var $form = $(form);
        var data = $form.serialize();
        data += '&action=' + btn.name;
        var url = $form.attr('action');

        var self = this;
        //self._disableBtn(btn, true);

        if (document.DEBUG){
            console.log(url);
            console.log(data);
		}
        return $.ajax({
            type: "POST",
            url: url,
            data: data,
            success: function(d) {
				document.DEBUG && console.log(d);
				
                //self._disableBtn(btn, false);

                var data = $.parseJSON(d);
                if (data.error){
                    Updater.prototype.ShowError(data.error);
                }
            }
        });
    },

    _disableBtn: function(btn, disable){
        var $btn = $(btn);
        if (disable){
            $btn.attr("disabled", "disabled");
            $btn.addClass("ui-state-disabled");
        }
        else {
            $btn.removeAttr("disabled");
            $btn.removeClass("ui-state-disabled");
        }
    }
};

// contact, motion, etc.
function Device() {}
Device.prototype = new Form();
jQuery.extend(Device.prototype, {
    _startTimerBtnName: null,
    _stopTimerBtnName: null,
    _isOpened: null,

    Init: function(deviceForm, timersPool, startTimerBtnName, stopTimerBtnName){
        this._startTimerBtnName = startTimerBtnName;
        this._stopTimerBtnName = stopTimerBtnName;

        var timer = new Timer();
        var timerId = +deviceForm.find('[name=zone]').val();
        var timeElement = deviceForm.find('.timer').text("0:00");
        timer.Init(timerId, timeElement);
        timersPool[timerId] = timer;

        this._bindEvents(deviceForm, timersPool);
    },

    _bindEvents: function(deviceForm, timersPool){
        var self = this;
        deviceForm.on('submit', function(e){
            var $form = $(this);
            var id = +$form.find('[name=zone]').val();
            var timeElement = $form.find('.timer');
            var action = self._setTimersBehavior(e, timersPool, id, timeElement, $form);
            if (action == "enroll" && !self._confirm("Are you sure you want to enroll this device?")){
                e.preventDefault();
                return;
            }
            action == self._stopTimerBtnName ? e.preventDefault() : self.Submit(this, e);
        });

        deviceForm.on('change', function(e){
            self.Submit(this, e);
        });
    },

    _confirm: function(text){
        return confirm(text);
    },

    _setTimersBehavior: function(e, timersPool, id, timeElement, form){
        var self = this;
        var action = e.originalEvent.explicitOriginalTarget.name;
        var timer = timersPool[id];

        if (action == self._startTimerBtnName){
            if (!timer.IsTiming && !self._isOpened){
                timer.StartTimer(timersPool);
            }
            self._isOpened = !self._isOpened;
            var openClose = form.find('[name='+self._startTimerBtnName+']');
            if (openClose.val() != "Activate") 
				openClose.val(self._isOpened ? "Close" : "Open");
        }

        if (action == self._stopTimerBtnName){
            timer.IsTiming ? timer.StopTimer(timersPool) : timeElement.text("0:00");
        }
        return action;
    }
});

// panel UI block
function Panel() {}
Panel.prototype = new Form();
jQuery.extend(Panel.prototype, {
	settings: {
		screenUpdateInterval: 1000,
		enableScreenUpdate: false,
	},
	
	_actionUrl: null,
	_screenUpdaterIdx: null,
	
    PanelBlock: null,
    MainForm: null,
    Screen: null,
    HideBtn: null,
    CustomActionsList: null,
    btnRunCustom: null,
	
	_isVisible: false,

    Init: function(settings){
		$.extend(this.settings, settings);
		
		this._initControls();
		this._actionUrl = this.MainForm.attr('action');

		this._bindEvents();
        this._initShowHideBtn();
		this._initCustomActions();
		this.StartScreenUpdate();
    },
	
	_initControls: function(){
		this.PanelBlock = $('#PanelUI');
		var block = this.PanelBlock;
		block.draggable();
		/*
		block.offset(JSON.parse($.cookie("panel-position")));
		block.draggable({
			stop: function(){
				var offset = JSON.stringify(block.offset());
				$.cookie("panel-position", offset);
			}
		});
		*/        
        this.MainForm = block.find("#Panel");
        this.Screen = block.find('#panel_screen');
        this.HideBtn = block.find("#hidePanel");
        this.CustomActionsList = block.find('#custom_action');
        this.btnRunCustom = block.find('#custom');
	},
	
	_bindEvents: function() {
		var self = this;
		
        self.MainForm.on('submit', function(e){
            self.Submit(this, e).then(self.updatePanelScreen);
        });
		
        self.CustomActionsList.on('change', function(){
			self._disableCustomAction(this);
        });
	},
	
	_disableCustomAction: function(dropdown) {
		var disabled = dropdown.selectedIndex == 0;
		this._disableBtn(this.btnRunCustom, disabled);
	},	
	
	_initCustomActions: function() {
		this._disableCustomAction(this.CustomActionsList);
		
		var link = $('<a/>', { id: 'customActions', href: '#', text: 'More actions...' });
		var block = $('<tr/>').append($('<td/>').append(link));
		var tr = this.CustomActionsList.closest('tr');
		tr.hide().before(block).after($('<p id="construct">Under construction...</p>').hide());
		link.on('click', function() {
			this.hide().parent().find('#construct').show();
		});		
	},
	
    _initShowHideBtn: function(){
        var self = this;
        self._isVisible = true;
        self.HideBtn.text("Hide");
		
        self.HideBtn.on('click', function() {
            if (self._isVisible){
                self.MainForm.hide();
                self.HideBtn.text("Show");
                self.StopScreenUpdate();
            }
            else {
                $.get('pm30/virt');
                self.MainForm.show();
                self.HideBtn.text("Hide");
                self.StartScreenUpdate();
            }
            self._isVisible = !self._isVisible;
        });
    },
	
	StartScreenUpdate: function() {
		if (this.settings.enableScreenUpdate){
			this._screenUpdaterIdx = this.StartUpdater(this._actionUrl, $.proxy(this._updatePanelScreen, this), this.settings.screenUpdateInterval);
		}
	},
	StopScreenUpdate: function() {
		this.StopUpdater(this._screenUpdaterIdx);
	},	
	_updatePanelScreen: function(data) {	
        this.Screen.text(data.screen);
    }
});

// ipmp log
function IpmpLog() {}
IpmpLog.prototype = new Form();
jQuery.extend(IpmpLog.prototype, {
	settings: {
		logUpdateInterval: 1000,
	},
	
    btnRun: null,
    btnStop: null,
    MainForm: null,
    TextArea: null,
	
	_actionUrl: null,
	_logUpdaterIdx: null,

    Init: function(settings){
		$.extend(this.settings, settings);
	
        this.MainForm = $('#IPMPlog');
        var main = this.MainForm;
		this._actionUrl = main.attr('action');
        this.btnRun = main.find("#Run");
        this.btnStop = main.find("#Stop");
        this.TextArea = main.find('#log');
		
		this._bindEvents();

        this._disableBtn(this.btnStop, true);
    },
	
	_bindEvents: function(){
		var self = this;
		self.MainForm.on('submit', function(e){
			// init log on server side (create or dispose)
			self.Submit(this, e)
				.then(function() { self._logHandling(e); });
        });
	},
	
	_logHandling: function(e){
		this._handleButtons(action);		
		
		var action = e.originalEvent.explicitOriginalTarget.name;
		switch(action) {
			case "run":
				this.StartLogUpdate();
				break;
			case "stop":
				this.StopLogUpdate();
				break;
		}	
	},
	
	_handleButtons: function(action){
		this._disableBtn(this.btnRun, action == "run");
		this._disableBtn(this.btnStop, action == "stop");
	},
	
	StartLogUpdate: function(){
		this._logUpdaterIdx = this.StartUpdater(this._actionUrl, $.proxy(this._updateLog, this), this.settings.logUpdateInterval);
	},	
	StopLogUpdate: function(){
		this.StopUpdater(this._logUpdaterIdx);
	},	
	_updateLog: function(data){
		var lines = data.lines;
		this.TextArea.text(lines.join('\n'));
		this.TextArea.scrollTop(this.TextArea[0].scrollHeight);
	}	
});