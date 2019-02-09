$(function () {
    var stream_cmd = ['streamon', 'streamoff'];
    var info_cmd = ['battery?', 'speed?', 'temp?'];
    var tracking_cmd = ['streaming', 'test', 'tracking'];
    var detection_cmd = ['async', 'sync', 'object_detection',
        'age_gender_detection', 'face_detection',
        'emotions_detection', 'head_pose_detection',
        'facial_landmarks_detection'];
    var connect_cmd = ['command'];
    var control_cmd = ['takeoff', 'land', 'up', 'down', 'left', 'right', 'forward', 'back', 'cw', 'ccw', "flip"];
    var flip_cmd = ['flip'];
    var info_flg = 0;
    var url = "";
    $(function () {
        // info_flg is used for getting  information correctly of tello per certain interval.
        // i don't think this is smart way..
        setInterval(function () {
            if (info_flg == 1) {
                post('/info', JSON.stringify({ "command": "battery?" }));
            } else if (info_flg == 2) {
                post('/info', JSON.stringify({ "command": "speed?" }));
            } else if (info_flg == 3) {
                post('/info', JSON.stringify({ "command": "temp?" }));
                info_flg = 0;
            }
            info_flg++;
        }, 5000);
    });
    $(function () {
        var n = 20;
        var speed_range = 20;
        $('#speed').val(n);
        $('#speed-plus.plus').on('click', function () {
            if (n < 100) {
                $('#speed').val(n = n + speed_range);
                command = JSON.stringify({ "command": "speed " + n });
                post('/tellooo', command);
            }
        });
        $('#speed-min.min').on('click', function () {
            if (n > 20) {
                $('#speed').val(n = n - speed_range);
                command = JSON.stringify({ "command": "speed " + n });
                post('/tellooo', command);
            }
        });
    });
    $(function () {
        var n = 20;
        var distance_range = 20;
        $('#distance').val(n);
        $('#distance-plus.plus').on('click', function () {
            if (n < 100) {
                $('#distance').val(n = n + distance_range);
                command = JSON.stringify({ "command": "distance " + n });
                post('/tellooo', command);
            }
        });
        $('#distance-min.min').on('click', function () {
            if (n > 20) {
                $('#distance').val(n = n - distance_range);
                command = JSON.stringify({ "command": "distance " + n });
                post('/tellooo', command);
            }
        });
    });
    $('.btn').on('click', function () {
        var command = JSON.stringify({ "command": $('#' + $(this).attr('id')).val() });
        if (JSON.parse(command).command == "") {
            var command = JSON.stringify({ "command": $(this).find('input').val() });
        }
        //console.log(command, tracking_cmd.includes(JSON.parse(command).command))
        if (info_cmd.includes(JSON.parse(command).command)) {
            url = '/info';
        } else if (flip_cmd.includes(JSON.parse(command).command)) {
            url = '/flip';
        } else if (connect_cmd.includes(JSON.parse(command).command)) {
            url = '/tellooo';
        } else if (control_cmd.includes(JSON.parse(command).command) || JSON.parse(command).command.match(/flip [l,r,f,b]/)) {
            url = '/tellooo';
        } else if (stream_cmd.includes(JSON.parse(command).command)) {
            url = '/tellooo';
        } else if (tracking_cmd.includes(JSON.parse(command).command)) {
            url = '/tracking';
        } else if (detection_cmd.includes(JSON.parse(command).command)) {
            url = '/detection';
        }
        post(url, command);
    });
    function post(url, command) {
        $.ajax({
            type: 'POST',
            url: url,
            data: command,
            contentType: 'application/json',
            timeout: 10000
        }).done(function (data) {
            var sent_cmd = JSON.parse(command).command;
            var tello_res = JSON.parse(data.ResultSet).result;
            var is_connected = JSON.parse(data.ResultSet).is_connected;
            var is_streamon = JSON.parse(data.ResultSet).is_streamon;
            var is_stream = JSON.parse(data.ResultSet).is_stream;
            var is_test = JSON.parse(data.ResultSet).is_test;
            var is_tracking = JSON.parse(data.ResultSet).is_tracking;
            var is_async_mode = JSON.parse(data.ResultSet).is_async_mode;
            var flip_code = JSON.parse(data.ResultSet).flip_code;
            var is_obj_det = JSON.parse(data.ResultSet).is_object_detection;
            var is_face_det = JSON.parse(data.ResultSet).is_face_detection;
            var is_ag_det = JSON.parse(data.ResultSet).is_age_gender_detection;
            var is_em_det = JSON.parse(data.ResultSet).is_emotions_detection;
            var is_hp_det = JSON.parse(data.ResultSet).is_head_pose_detection;
            var is_lm_det = JSON.parse(data.ResultSet).is_facial_landmarks_detection;

            //console.log(JSON.parse(data.ResultSet));
            if (is_connected) {
                if (connect_cmd.includes(sent_cmd)) {
                    $("#res").text(sent_cmd + ":" + tello_res);
                    if (!is_streamon) {
                        $('.img-fluid').attr('src', '../../static/images/tello_c.png');
                        $("#command").attr('class', 'btn btn-success');
                        $("#res").text('Click streamon!');
                    }
                }
                // face analytics button control
                if (is_face_det) {
                    $("#is_face_detection").attr("disabled", false);
                }
                if (!is_face_det) {
                    $("#is_face_detection").attr("disabled", true);
                }
                // requst info of tello
                if (sent_cmd == "battery?") {
                    $("#info-battery").text(sent_cmd + ":" + tello_res);
                }
                if (sent_cmd == "speed?" || sent_cmd.match(/speed \d+/)) {
                    sent_cmd = sent_cmd.split(" ", 1)[0]
                    $("#info-speed").text(sent_cmd + ":" + tello_res);
                }
                if (sent_cmd == "temp?") {
                    $("#info-temp").text(sent_cmd + ":" + tello_res);
                }
                // async/sync buttons contorol
                if (is_stream || is_tracking) {
                    $("#is_async").attr("disabled", true);
                }
                if (is_obj_det || is_face_det) {
                    $("#is_async").attr("disabled", false);
                    if (sent_cmd == 'async') {
                        $("#async").attr('class', 'btn btn-danger btn-sm');
                        $("#sync").attr('class', 'btn btn-secondary btn-sm');
                    }
                    if (sent_cmd == 'sync') {
                        $("#async").attr('class', 'btn btn-secondary btn-sm');
                        $("#sync").attr('class', 'btn btn-danger btn-sm');
                    }
                    //console.log(sent_cmd, detection_cmd.includes(sent_cmd));
                    $("#res").text("async:" + is_async_mode + " ssd:" + is_obj_det + " face:" + is_face_det + " ag:" + is_ag_det + " em:" + is_em_det + " hp:" + is_hp_det + " lm:" + is_lm_det);
                }
                //if (sent_cmd == 'object_detection') {
                //    $("#is_face_detection").attr("disabled", true);
                //    $("#is_async").attr("disabled", false);
                //}
                if (control_cmd.includes(sent_cmd) || tracking_cmd.includes(sent_cmd) || sent_cmd.match(/flip [l,r,f,b]/)) {
                    $("#res").text(sent_cmd + ":" + tello_res);
                }
                if (stream_cmd.includes(sent_cmd)) {
                    $("#res").text(sent_cmd + ":" + tello_res);
                    $(function () {
                        setTimeout(function () {
                            window.location.href = window.location.href
                        }, 1000);
                    });
                }
            } else {
                $("#res").text('Click connect at first!');
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            $("#res").text(textStatus + ":" + jqXHR.status + " " + errorThrown);
        });
        return false;
    }
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });
});

