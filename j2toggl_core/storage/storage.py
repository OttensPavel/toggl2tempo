from j2toggl_core.worklog import WorkLog


class StorageBase:
    def add(self, worklog: WorkLog):
        raise NotImplementedError

    def get_second_id(self, master_id: int) -> int:
        raise NotImplementedError

    def get_master_id(self, second_id: int) -> int:
        raise NotImplementedError

    def delete(self, worklog: WorkLog):
        raise NotImplementedError
