// base class
function Form() {}
Form.prototype = {
    Submit: function(form, evt){
        evt.preventDefault();
        var btn = evt.originalEvent.explicitOriginalTarget;

        var $form = $(form);
        var data = $form.serialize();
        data += '&action=' + btn.name;
        var url = $form.attr('action');

        var self = this;
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

                var data = $.parseJSON(d).error;
                if (data.error){
                    alert(data.error);
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
}

// contact, motion, etc.
function Device() {}
Device.prototype = new Form();
jQuery.extend(Device.prototype, {
    Init: function(){
        var self = this;
        $('.contactForm').on('submit', function(e){
            self.Submit(this, e);
        });
    }
});

// panel UI block
function Panel() {}
Panel.prototype = new Form();
jQuery.extend(Panel.prototype, {
    _doUpdate: false,
    _timerId: 0,
    _checkInterval: 500,
    PanelBlock: null,
    MainForm: null,
    Screen: null,
    HideBtn: null,
    Visible: false,
    EnableScreenUpdate: false,
    CustomActionsList:null,
    btnRunCustom: null,

    Init: function(){
        var self = this;
        self.PanelBlock =  $('#PanelUI').draggable();
        var block = self.PanelBlock;
        self.MainForm = block.find("#Panel");
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
            url : "panel_view",
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
})

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
                    var action = e.originalEvent.explicitOriginalTarget.name;
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
