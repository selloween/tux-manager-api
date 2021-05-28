from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from safrs import SAFRSBase, SAFRSAPI, jsonapi_rpc

import config
from gen_csr import gen_csr

db = SQLAlchemy()


class Tag(SAFRSBase, db.Model):
    __tablename__ = "tag"
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(80), nullable=False)


class TagItem(SAFRSBase, db.Model):
    __tablename__ = "tagitem"
    ti_id = db.Column(db.Integer, primary_key=True)
    ti_name = db.Column(db.String(80), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.tag_id"))
    tag = db.relationship("Tag")


class TagItem2TagItem(SAFRSBase, db.Model):
    __tablename__ = "tagitem2tagitem"
    ti2ti_id = db.Column(db.Integer, primary_key=True)
    ti_src_id = db.Column(db.Integer, db.ForeignKey('tagitem.ti_id'), nullable=False)
    ti_dst_id = db.Column(db.Integer, db.ForeignKey('tagitem.ti_id'), nullable=False)
    ti_src = db.relationship("TagItem", foreign_keys=[ti_src_id])
    ti_dst = db.relationship("TagItem", foreign_keys=[ti_dst_id])


class RelType(SAFRSBase, db.Model):
    __tablename__ = "reltype"
    reltype_id = db.Column(db.Integer, primary_key=True)
    reltype_type = db.Column(db.String(80), nullable=False)


class Csr(SAFRSBase, db.Model):
    __tablename__ = "csr"
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(80), nullable=False)
    csr = db.Column(db.Text())

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
    api.expose_object(Csr)
    print("Starting API: http://{}:{}/{}".format(HOST, PORT, API_PREFIX))


def create_app(config_filename=None, host="localhost"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        create_api(app, host)
        return app


app = create_app(host="localhost")


if __name__ == "__main__":
    # Start application
    app.run(port=5010, debug=True)
