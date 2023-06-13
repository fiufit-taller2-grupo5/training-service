import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

config = {
    "type": "service_account",
    "project_id": "fiufit-93740",
    "private_key_id": "6968e6b01bd17d5187063933f69bfd1fa65360bf",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQD8fllvppP0VRI8\n9MmdtwiT9rGX0+sZaJnf2ZNm1DgHVLOIWotoE+BGxWX5+XsNh29xO/CXAh5ySz7S\nYK5z/+bdj6tNhFjyesd78LcQavXkxHHjF/51rVV0eUlidZv4VAnw1C4b5ZpQgNpr\nvWvASPCqhfwufYXLc+dENraPiV9zQI+DtuInY6sv3idAC9QhtiESIK35Xq1ZntIa\nlnr00cwDkazd4Nz9sZXiT/XYoCzB6C3DSr6Ew35YZjcR0OL8kfCrdKFkiBw0lxo1\njEVdymb5ElPY2m/To0wzNYdJhwex7Sum19qKXIp8lnlWbL0nvFCClgnI1mdCOLz0\naAAQppyFAgMBAAECggEAGTMQAINmxU4fP5urqpSro77NeypwjozgvJVVr3/TJrIm\np99nhefj7JRDaPcj95XygqHZkWyp9ry5RJxXFOcvlqHB1j709KBZ2+4KizYtm9sa\nRbCtmfeGbZU0RIIZ4qcaheFbR7f61nmBsxqI0DxHXrF4GXi4G3XSGT3/quQqNVGD\nsX+2o1kLOFkYI4cQLeIb8kkA/jeSDGj1Nk1v2WWJz98GvszsUBXsxbgkKlnrw9gR\n3dWTb4nTGFz9P+dMSVkd9am1uOI0kKxVU4+NYpcWvsc723AfRNx4DskKJbxkS1Aq\nXOEoGkRBoeMYMOArpvB+sdYRuicCODnGlvJz1PzmIQKBgQD/eZI8si3xH4XjwEan\nlqy2YSJmkv6QPZz9FASSvFIepkc/HF+y83KCq3cc5GgWR8jTaUswmch1ajy3YGvf\nLc42qPCfRmcqcHTxT+v/SelkbRRYREavRIGg7WTLzC0Q7bD9uqcIjcBd9r7qXlMy\nQvdmrUc+oEqVZCr6wVBrVJM0pQKBgQD9AzWZGOSRpaOO7OlwLYWXuaefnvLgHxbQ\n1l04QdZ9WpixYC2geZuYk1ikQNcvLF557k8TIjSnBCKvJMj1kyjFpw9oPPQkSjV5\nmLFes1BMjfgvUNPztvnKELqcjxH3U3d6baSayKsC+w4gFDyNMFJd/s373keu8i5o\nb05ic+7iYQKBgQCbcpilr/E+Z2TriMI1FPxwWLg627RjhenxH+4MbuQ03A47+4LL\ne1Aw7C4k+WHQNMugv8/NebU8pHDfT58zhEaWgcMv1wHNE/JEJtI9WvbVcX3Qm3K7\nEJ8jkW8khk7hnw9zw9AA52emhQ3zw4Mx8QdihYr1M0lOj02LmHbbZ/HONQKBgQCM\nwfhTkBG5JZl0rkDAc9LasiKbHuan4SPkUx3Ram9Vlc1VANjhakYx/+dUme4dBGYb\nF4VOc70vHZHeNmzGknQgYeykZSS9+7r8RwKGWOPXczQbvq/r6mPVErF+3+ly2zCh\nH9ZvdiwNoHYfSqLVOYjZWiRmdycSIRHIcAP/qdfAgQKBgQC252H5p7ltw/mjsE2c\no6FUx5CVIXF/zqTUwzZ8q83q2/C88+9fRi2+kZ8rR5UgdmVWaqGfiLEC86LvcqRO\nXe6dLIBGMl71cdkRYHlxV9iYWuzffzp3BlhC/W6XNejVr8u7dv8XQ1TOsW4SsfHO\n5/dlSBSaX5YYENcCqy/xPMGqQA==\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-vpty6@fiufit-93740.iam.gserviceaccount.com",
    "client_id": "109439978303683981810",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-vpty6%40fiufit-93740.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(config)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'fiufit-93740.appspot.com'
})

bucket = storage.bucket()


def make_dir(dir_name):
    blob = bucket.blob(dir_name)
    blob.upload_from_string('')


def upload_file(file, file_name):
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.upload_from_file(file, content_type='image/jpeg')

    # Make the blob public
    blob.make_public()

    # Get the public URL
    public_url = blob.public_url
    return public_url