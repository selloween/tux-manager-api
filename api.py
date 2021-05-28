from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from safrs import SAFRSBase, SAFRSAPI, jsonapi_rpc
from gen_csr import gen_csr
import datetime
import config

db = SQLAlchemy()


class Tag(SAFRSBase, db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)


class TagItem(SAFRSBase, db.Model):
    __tablename__ = "tagitem"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), nullable=False)
    tag = db.relationship("Tag")


class TagItem2TagItem(SAFRSBase, db.Model):
    __tablename__ = "tagitem2tagitem"
    id = db.Column(db.Integer, primary_key=True)
    tagitem_src_id = db.Column(db.Integer, db.ForeignKey('tagitem.id'), nullable=False)
    tagitem_dst_id = db.Column(db.Integer, db.ForeignKey('tagitem.id'), nullable=False)
    tagitem_src = db.relationship("TagItem", foreign_keys=[tagitem_src_id])
    tagitem_dst = db.relationship("TagItem", foreign_keys=[tagitem_dst_id])
    reltype_id = db.Column(db.Integer, db.ForeignKey("reltype.id"), nullable=False)
    reltype = db.relationship("RelType")


class RelType(SAFRSBase, db.Model):
    __tablename__ = "reltype"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

#ondelete="CASCADE"
class Csr(SAFRSBase, db.Model):
    __tablename__ = "csr"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.datetime.now())
    domain = db.Column(db.String(80), nullable=False)
    csr = db.Column(db.Text())
    http_methods = {"GET", "POST"}  # only allow GET and POST

    @jsonapi_rpc(http_methods=['POST'])
    def generate_csr(self):
        '''
            description : Generate CSR
        '''
        new_csr = gen_csr(self.domain)
        update_csr = Csr(id=self.id, domain=self.domain, csr=new_csr)

        return {update_csr}


def create_api(app, HOST="localhost", PORT=5010, API_PREFIX=""):
    api = SAFRSAPI(app, host=HOST, port=PORT, prefix=API_PREFIX)
    api.expose_object(Tag)
    api.expose_object(TagItem)
    api.expose_object(TagItem2TagItem)
    api.expose_object(RelType)
    api.expose_object(Csr)
    print("Starting API: http://{}:{}/{}".format(HOST, PORT, API_PREFIX))


def create_app(config_filename=None, host="localhost"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

        # Populate db with default tags
        server_tag = {
            "id": 1,
            "name": "server"
        }
        ip_tag = {
            "id": 2,
            "name": "ip"
        }
        cert_tag = {
            "id": 3,
            "name": "cert"
        }
        owner_tag = {
            "id": 4,
            "name": "owner"
        }
        stage_tag = {
            "id": 5,
            "name": "stage"
        }
        patch_group_tag = {
            "id": 6,
            "name": "patch_group"
        }

        tags = (server_tag, ip_tag, cert_tag, owner_tag, stage_tag, patch_group_tag)

        for tag in tags:
            Tag(id=tag["id"], name=tag["name"])



        create_api(app, host)
        return app


app = create_app(host="localhost")


if __name__ == "__main__":
    # Start application
    app.run(port=5010, debug=True)
