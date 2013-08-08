// base class
function Form() {}
Form.prototype = {
    Submit: function(form, evt){
        evt.preventDefault();

        var self = this;
        var btn = self._getSubmitButton(evt);

        var $form = $(form);
        var data = $form.serialize();
        data += '&action=' + btn.name;
        var url = $form.attr('action');

        self._disableBtn(true);

        if (document.DEBUG)
            console.log(url);
            console.log(data);

        return $.ajax({
            type : "POST",
            cache : false,
            url : url,
            data : data,
            success : function(d) {
                self._disableBtn(false);

                var error = $.parseJSON(d).error;
                if (error){
                    alert(error);
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
    },

    _getSubmitButton: function(evt){
        return evt.originalEvent.explicitOriginalTarget;
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
        var self = this;
        self._startTimerBtnName = startTimerBtnName;
        self._stopTimerBtnName = stopTimerBtnName;

        var timer = new Timer();
        var timerId = +deviceForm.find('[name=zone]').val();
        var timeElement = deviceForm.find('.timer').text("0:00");
        timer.Init(timerId, timeElement);
        timersPool[timerId] = timer;

        self._bindEvents(deviceForm, timersPool);
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
        var action = self._getSubmitButton(e).name;
        var timer = timersPool[id];

        if (action == self._startTimerBtnName){
            if (!timer.IsTiming && !self._isOpened){
                timer.StartTimer(timersPool);
            }
            var openClose = form.find('[name='+self._startTimerBtnName+']');
            if (openClose.val() != "Activate"){
				self._isOpened = !self._isOpened;
				openClose.val(self._isOpened ? "Close" : "Open");
			}				
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
    _doUpdate: false,
    _timerId: 0,
    _checkInterval: 1000,
    PanelBlock: null,
    MainForm: null,
    Screen: null,
    HideBtn: null,
    Visible: false,
    EnableScreenUpdate: false,
    CustomActionsList:null,
    btnRunCustom: null,
	_actionUrl: null,

    Init: function(){
        var self = this;
        self.PanelBlock =  $('#PanelUI').draggable();
        var block = self.PanelBlock;
        self.MainForm = block.find("#Panel");
		self._actionUrl = self.MainForm.attr('action');
        self.Screen = block.find('#panel_screen');
        self.HideBtn = block.find("#hidePanel");
        self.CustomActionsList = block.find('#custom_action');
        self.btnRunCustom = block.find('#custom');

        self.MainForm.on('submit', function(e){
            self.Submit(this, e);
        });
        self.CustomActionsList.on('change', function(){
            var disabled = this.selectedIndex == 0
            self._disableBtn(self.btnRunCustom, disabled);
        });

        self._initShowHideBtn();
        self._disableBtn(self.btnRunCustom, true);
		
		self.StartUpdating();
    },

    _initShowHideBtn: function(){
        var self = this;
        self.Visible = true;
        self.HideBtn.text("Hide");
        self.HideBtn.on('click', function() {
            if (self.Visible){
                self.MainForm.hide();
                self.HideBtn.text("Show");
                self.StopUpdating();
            }
            else {
                self.MainForm.show();
                self.HideBtn.text("Hide");
                self.StartUpdating();
            }
            self.Visible = !self.Visible;
        });
    },

    StopUpdating: function() {
        this._doUpdate = false;
    },

    StartUpdating: function() {
        if (this.EnableScreenUpdate && !this._doUpdate){
            this._doUpdate = true;
            this._initUpdatingThread();
        }
    },

    UpdatePanelScreen: function() {
        var self = this;
        $.ajax({
            type : "POST",
            url : self._actionUrl,
            success : function(data) {
                self.Screen.text(data);
            }
        });
    },

    _initUpdatingThread: function(){
        var self = this;
        this._timerId = setTimeout(function () {
            self._timedOut.call(self);
        }, this._checkInterval);
    },

    _timedOut: function() {
        if (this.EnableScreenUpdate && this._doUpdate) {
            this.UpdatePanelScreen();
            this._initUpdatingThread();
        } else {
            clearTimeout(this._timerId);
        }
    }
});

// contact, motion, etc.
function IpmpLog() {}
IpmpLog.prototype = new Form();
jQuery.extend(IpmpLog.prototype, {
    btnRun: null,
    btnStop: null,
    MainForm: null,
    TextArea: null,

    Init: function(){
        var self = this;
        self.MainForm = $('#IPMPlog');
        var main = self.MainForm;
        self.btnRun = main.find("#Run");
        self.btnStop = main.find("#Stop");
        self.TextArea = main.find('#log');

        self.MainForm.on('submit', function(e){
            self.Submit(this, e)
                .then(function(data){
                    var action = self._getSubmitButton(e).name;
                    self._disableBtn(self.btnRun, action == "run");
                    self._disableBtn(self.btnStop, action == "stop");

                    var lines = $.parseJSON(data).lines;
                    self.TextArea.text(lines.join('\n'));
                    self.TextArea.scrollTop(self.TextArea[0].scrollHeight);
                });
        });

        self._disableBtn(self.btnStop, true);
    }
});
