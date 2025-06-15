from sqlalchemy.orm import aliased
from sqlalchemy import func
from Model.ImageHistory import ImageHistory  # ✅ Correct import
from config import db  # ensure db is available

class ImageHistoryController:
    @staticmethod
    def get_latest_inactive_non_deleted_images():
        subquery = db.session.query(
            ImageHistory.id.label('image_id'),
            func.max(ImageHistory.version_no).label('max_version')
        ).filter(
            ImageHistory.is_Active == False,
            ImageHistory.is_deleted == False
        ).group_by(ImageHistory.id).subquery()

        IH = aliased(ImageHistory)

        results = db.session.query(
            IH.id,
            IH.path,
            IH.version_no
        ).join(
            subquery,
            (IH.id == subquery.c.image_id) & (IH.version_no == subquery.c.max_version)
        ).filter(
            IH.is_Active == False,
            IH.is_deleted == False
        ).all()
        print (results)
        return [{'id': r.id, 'path': r.path, 'version_no': r.version_no} for r in results]
        
