from database import DBCommunicator
from graphic import SingletonDrawer, ZipVar
import constants as cns


if __name__ == "__main__":
    comm = DBCommunicator('localhost', cns.DATABASE_NAME)
    draw = SingletonDrawer()
    while True:
        pts = comm.get_points(cns.MEASURE_NAME)
        pts_nm_dict = {}
        for pt_dict in pts:
            tm = pt_dict.pop("time")
            for a in pt_dict:
                if pts_nm_dict.get(a) is None:
                    pts_nm_dict[a] = ZipVar(a, [], [])
                pts_nm_dict[a].value.append(pt_dict[a])
                pts_nm_dict[a].timestamps.append(tm)

        draw.update_vars(pts_nm_dict.values())
        draw.draw()
        draw.pause()
