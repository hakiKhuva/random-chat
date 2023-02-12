import { io } from "https://cdn.socket.io/4.4.1/socket.io.esm.min.js";

window.mdata = null;

(() => {
    const message_form = document.querySelector("#message-form")
    const message_text_element = document.querySelector("#message-to-send")
    const message_send_btn = document.querySelector("#message-send-btn")
    const message_attach_file = document.querySelector("#message-attach-file")

    const connect_btn = document.querySelector("#connect-btn")
    const disconnect_btn = document.querySelector("#disconnect-btn")
    const dl_mode_btn = document.querySelector("#dl-mode-btn")

    let current_theme = {
        "bg": "#222",
        "fg": "#eee"
    }

    function returnFileSize(number) {
        if (number < 1024) {
            return `${number} bytes`;
        } else if (number >= 1024 && number < 1048576) {
            return `${(number / 1024).toFixed(1)} KB`;
        } else if (number >= 1048576) {
            return `${(number / 1048576).toFixed(1)} MB`;
        }
    }

    const message_board = document.querySelector("#message-container")

    const disable_connect_btn = () => {
        connect_btn.disabled = true
    }

    const process_message_elements = (process_type = "start") => {
        message_text_element.disabled = process_type === "start" ? false : true;
        message_send_btn.disabled = process_type === "start" ? false : true;
        message_attach_file.disabled = process_type === "start" ? false : true;
        disconnect_btn.disabled = process_type === "start" ? false : true;

        connect_btn.disabled = process_type === "start" ? true : false;

        message_text_element.value = ''
    }

    const clear_message_board = () => {
        message_board.innerHTML = ''
    }

    const create_message_element = (message) => {
        const div = document.createElement("div")
        div.textContent = message;
        div.classList.add("msg")

        return div
    }

    const create_file_message_element = (message) => {
        const div = document.createElement("div")
        div.className = "file msg recv"

        const div_head = document.createElement("div")
        div_head.className = "upper-head"
        div_head.innerHTML = (message.s_name || "Me")+":"

        const div_inner = document.createElement("div")
        div_inner.className = "inner-file"

        const div_name_size = document.createElement("div")
        div_name_size.className = "name-size"

        const name_span = document.createElement("span")
        name_span.innerText = message.name
        const size_span = document.createElement("span")
        size_span.innerText = " (" + message.size + ")"

        div_name_size.append(name_span, size_span)

        const div_type = document.createElement("div")
        div_type.className = "type"
        div_type.innerText = message.mimetype

        div_inner.append(div_head, div_name_size, div_type)

        const anchor_download = document.createElement("a")
        anchor_download.className = "file-dl-link"
        anchor_download.textContent = 'Download'
        anchor_download.href = message.data;
        anchor_download.setAttribute("download", message.name)

        div.append(div_inner, anchor_download)

        return div;
    }

    const get_last_message_node = () => {
        if (message_board.childNodes.length > 0) {
            return message_board.childNodes[0]
        }
        return null
    }
    const add_element_to_message_board = (element) => {
        const last_message_node = get_last_message_node()

        if (last_message_node === null) {
            message_board.append(element)
        } else {
            last_message_node.insertAdjacentElement("beforebegin", element)
        }

        message_board.scrollTo({
            top: message_board.scrollHeight,
            behavior: "smooth"
        })
    }
    const add_sent_message = (message) => {
        if (message.mimetype === "text") {
            const element = create_message_element(`Me: ${message.data}`)
            element.classList.add("sent")
            add_element_to_message_board(element)
        } else {
            const element = create_file_message_element(message)
            element.classList.add("sent")
            add_element_to_message_board(element)
        }
    }
    const add_received_message = (s_name, message) => {
        if (message.mimetype === "text") {
            const element = create_message_element(`${s_name}: ${message.data}`)
            element.classList.add("recv")
            add_element_to_message_board(element)

            message_text_element.focus()
        } else {
            const element = create_file_message_element(message)
            element.classList.add("recv")
            add_element_to_message_board(element)

            message_text_element.focus()
        }
    }
    const set_status = (message) => {
        const element = create_message_element(message)
        element.classList.add("status")
        add_element_to_message_board(element)
    }

    const main = () => {
        let socketio = null;

        connect_btn.addEventListener("click", e => {
            if (socketio) return;

            disable_connect_btn()

            socketio = io();

            socketio.on("join-user", user => {
                if (user["status"] === "found") {
                    clear_message_board();

                    process_message_elements();
                }
            })

            socketio.on("disconnect", e => {
                process_message_elements("end")
                socketio.disconnect()
                socketio = null;
            })

            socketio.on("new-message", message_data => {
                add_received_message(message_data.s_name, message_data, message_data)
            })

            socketio.on("status-message", data => {
                set_status(data.message)
            })

            socketio.on("error", e => {
                console.log(e)
            })
            socketio.on("my error", e => {
                console.log(e)
            })
        })

        disconnect_btn.addEventListener("click", e => {
            if (!socketio) return;

            process_message_elements("end")
            socketio.disconnect()
            socketio = null;
            set_status("You're disconnected!")
        })

        message_form.addEventListener("submit", e => {
            e.preventDefault();
            if (!socketio) return;

            message_text_element.focus()
            let message = message_text_element.value;

            if (!message) {
                set_status("Could not send an empty message!")
                return;
            }

            socketio.emit("send-message", {
                "mimetype": "text",
                "data": message
            }, e => {
                add_sent_message({
                    "mimetype": "text",
                    "data": message
                })

                message_text_element.textContent = ''
                message_text_element.value = ''
                message_form.focus()
            })
            return;
        })

        message_attach_file.addEventListener("change", async (e) => {
            const FILES = e.target.files;

            if (FILES.length > 0) {
                const FILE = FILES[0]

                if (FILE.size > 10000000) {
                    alert('File must be smaller than 10MBs')
                    return
                }

                let result;
                var reader = new FileReader();
                reader.readAsDataURL(FILE);
                reader.onload = function (e) {
                    result = e.target.result.toString();

                    const data = {
                        "mimetype": FILE.type,
                        "name": FILE.name,
                        "size": returnFileSize(FILE.size),
                        "data": result
                    }

                    socketio.emit("send-message", data, e => {
                        add_sent_message(data)

                        message_text_element.textContent = ''
                        message_text_element.value = ''
                        message_form.focus()
                    })
                };
                return;
            }
        })

        dl_mode_btn.addEventListener("click", e => {
            e.preventDefault()
            document.documentElement.style.setProperty("--fg", current_theme.bg)
            document.documentElement.style.setProperty("--bg", current_theme.fg)
            let current_fg = current_theme.fg;
            current_theme.fg = current_theme.bg
            current_theme.bg = current_fg
        })
    }
    main();
})()