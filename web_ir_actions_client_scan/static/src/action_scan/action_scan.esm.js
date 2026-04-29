import {_t} from "@web/core/l10n/translation";
import {Component, onMounted} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {scanBarcode} from "@web/core/barcode/barcode_dialog";
import {url} from "@web/core/utils/urls";
import {useService} from "@web/core/utils/hooks";

export class ScanAction extends Component {
    static template = "web_ir_actions_client_scan.ScanPlaceholder";

    setup() {
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.orm = useService("orm");

        const fileExtension = new Audio().canPlayType("audio/ogg") ? "ogg" : "mp3";
        this.sounds = {
            error: new Audio(url(`/barcodes/static/src/audio/error.${fileExtension}`)),
            notify: new Audio(url(`/mail/static/src/audio/ting.${fileExtension}`)),
        };
        this.sounds.error.load();
        this.sounds.notify.load();

        onMounted(async () => {
            try {
                const value = await scanBarcode(this.env, "environment");
                if (value) {
                    const result = await this.orm.call(
                        this.props.action.res_model,
                        this.props.action.params.method,
                        [value],
                        {
                            context: this.props.action.context,
                        }
                    );
                    if (result && result.error) {
                        this.playSound("error");
                        this.notification.add(result.error, {type: "danger"});
                        this.onClickBack();
                        return;
                    }
                    if (result && result.type) {
                        this.playSound("notify");
                        this.actionService.doAction(result);
                        return;
                    }
                    this.playSound("error");
                    this.notification.add(_t("Unexpected server response"), {
                        type: "danger",
                    });
                    this.onClickBack();
                } else {
                    this.playSound("error");
                    this.notification.add(_t("Nothing scanned"), {type: "warning"});
                    this.onClickBack();
                }
            } catch (err) {
                console.error("Scan error:", err);
                this.playSound("error");
                this.notification.add(err.message || _t("Scanner not available"), {
                    type: "danger",
                });
                this.onClickBack();
            }
        });
    }

    playSound(type) {
        const soundType = type || "notify";
        this.sounds[soundType].currentTime = 0;
        this.sounds[soundType].play();
    }

    onClickBack() {
        this.actionService.restore();
    }
}

registry.category("actions").add("web_ir_actions_client_scan.scan", ScanAction);
