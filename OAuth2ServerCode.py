from flask import Flask, request, jsonify
import dotenv

app = Flask(__name__)

@app.route("/oauth2/code", methods=["GET"])
def oauth2_code():
    code = request.args.get("code")
    if code:
        dotenv.set_key("config.env", "OSM_OAUTH2_CODE", code)
        return jsonify({"code": code})
    return jsonify({"error": "Missing 'code' parameter"}), 400

if __name__ == "__main__":
    app.run()