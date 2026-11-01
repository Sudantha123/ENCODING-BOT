import datetime
import logging

import motor.motor_asyncio
from pymongo.errors import PyMongoError

LOGGER = logging.getLogger(__name__)


class Database:
    def __init__(self, uri, database_name):
        # Environment values often get copied with trailing newlines/spaces.
        # Strip them before passing the URI to PyMongo/Motor.
        uri = (uri or "").strip()
        database_name = (database_name or "").strip()

        if not uri:
            raise ValueError("MONGO_URI is missing or empty")
        if not database_name:
            raise ValueError("SESSION_NAME must contain a MongoDB database name")

        # Remove any accidental line breaks from the connection string.
        uri = "".join(uri.splitlines()).strip()

        self._client = motor.motor_asyncio.AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            retryWrites=True,
            w="majority",
        )
        self.db = self._client[database_name]
        self.col = self.db.users
        self.col2 = self.db.status

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            extensions='MKV',
            hevc=False,
            aspect=False,
            cabac=False,
            reframe='pass',
            tune=True,
            frame='source',
            audio='aac',
            sample='source',
            bitrate='source',
            bits=False,
            channels='source',
            drive=False,
            preset='sf',
            metadata=True,
            hardsub=False,
            watermark=False,
            subtitles=True,
            resolution='OG',
            upload_as_doc=False,
            crf=22,
            resize=False,
            thumbnail=None,
            motion_watermark=False,
            motion_opacity='50'
        )

    async def add_user(self, id):
        await self.col.update_one(
            {'id': int(id)},
            {'$setOnInsert': self.new_user(int(id))},
            upsert=True
        )

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)}, {'_id': 1})
        return user is not None

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def _get_user(self, id):
        user = await self.col.find_one({'id': int(id)})
        if not user:
            await self.add_user(int(id))
            user = await self.col.find_one({'id': int(id)})
        return user

    # Telegram Related
    async def set_upload_as_doc(self, id, upload_as_doc):
        await self.col.update_one({'id': id}, {'$set': {'upload_as_doc': upload_as_doc}}, upsert=True)

    async def get_upload_as_doc(self, id):
        user = await self._get_user(id)
        return user.get('upload_as_doc', False)

    # Encoding Settings
    async def set_resize(self, id, resize):
        await self.col.update_one({'id': id}, {'$set': {'resize': resize}}, upsert=True)

    async def get_resize(self, id):
        user = await self._get_user(id)
        return user.get('resize', 'resize')

    async def set_frame(self, id, frame):
        await self.col.update_one({'id': id}, {'$set': {'frame': frame}}, upsert=True)

    async def get_frame(self, id):
        user = await self._get_user(id)
        return user.get('frame', 'source')

    async def set_resolution(self, id, resolution):
        await self.col.update_one({'id': id}, {'$set': {'resolution': resolution}}, upsert=True)

    async def get_resolution(self, id):
        user = await self._get_user(id)
        return user.get('resolution', 'OG')

    async def set_bits(self, id, bits):
        await self.col.update_one({'id': id}, {'$set': {'bits': bits}}, upsert=True)

    async def get_bits(self, id):
        user = await self._get_user(id)
        return user.get('bits', False)

    async def set_subtitles(self, id, subtitles):
        await self.col.update_one({'id': id}, {'$set': {'subtitles': subtitles}}, upsert=True)

    async def get_subtitles(self, id):
        user = await self._get_user(id)
        return user.get('subtitles', False)

    async def set_samplerate(self, id, sample):
        await self.col.update_one({'id': id}, {'$set': {'sample': sample}}, upsert=True)

    async def get_samplerate(self, id):
        user = await self._get_user(id)
        return user.get('sample', '44.1K')

    async def set_extensions(self, id, extensions):
        await self.col.update_one({'id': id}, {'$set': {'extensions': extensions}}, upsert=True)

    async def get_extensions(self, id):
        user = await self._get_user(id)
        return user.get('extensions', 'MP4')

    async def set_bitrate(self, id, bitrate):
        await self.col.update_one({'id': id}, {'$set': {'bitrate': bitrate}}, upsert=True)

    async def get_bitrate(self, id):
        user = await self._get_user(id)
        return user.get('bitrate', '128')

    async def set_reframe(self, id, reframe):
        await self.col.update_one({'id': id}, {'$set': {'reframe': reframe}}, upsert=True)

    async def get_reframe(self, id):
        user = await self._get_user(id)
        return user.get('reframe', 'pass')

    async def set_audio(self, id, audio):
        await self.col.update_one({'id': id}, {'$set': {'audio': audio}}, upsert=True)

    async def get_audio(self, id):
        user = await self._get_user(id)
        return user.get('audio', 'dd')

    async def set_channels(self, id, channels):
        await self.col.update_one({'id': id}, {'$set': {'channels': channels}}, upsert=True)

    async def get_channels(self, id):
        user = await self._get_user(id)
        return user.get('channels', 'source')

    async def set_metadata_w(self, id, metadata):
        await self.col.update_one({'id': id}, {'$set': {'metadata': metadata}}, upsert=True)

    async def get_metadata_w(self, id):
        user = await self._get_user(id)
        return user.get('metadata', False)

    async def set_watermark(self, id, watermark):
        await self.col.update_one({'id': id}, {'$set': {'watermark': watermark}}, upsert=True)

    async def get_watermark(self, id):
        user = await self._get_user(id)
        return user.get('watermark', False)

    async def set_motion_watermark(self, id, motion):
        await self.col.update_one({'id': id}, {'$set': {'motion_watermark': motion}}, upsert=True)

    async def get_motion_watermark(self, id):
        user = await self._get_user(id)
        return user.get('motion_watermark', False)

    async def set_motion_opacity(self, id, opacity):
        await self.col.update_one({'id': id}, {'$set': {'motion_opacity': opacity}}, upsert=True)

    async def get_motion_opacity(self, id):
        user = await self._get_user(id)
        return user.get('motion_opacity', '50')

    async def set_preset(self, id, preset):
        await self.col.update_one({'id': id}, {'$set': {'preset': preset}}, upsert=True)

    async def get_preset(self, id):
        user = await self._get_user(id)
        return user.get('preset', 'sf')

    async def set_hardsub(self, id, hardsub):
        await self.col.update_one({'id': id}, {'$set': {'hardsub': hardsub}}, upsert=True)

    async def get_hardsub(self, id):
        user = await self._get_user(id)
        return user.get('hardsub', False)

    async def set_hevc(self, id, hevc):
        await self.col.update_one({'id': id}, {'$set': {'hevc': hevc}}, upsert=True)

    async def get_hevc(self, id):
        user = await self._get_user(id)
        return user.get('hevc', False)

    async def set_tune(self, id, tune):
        await self.col.update_one({'id': id}, {'$set': {'tune': tune}}, upsert=True)

    async def get_tune(self, id):
        user = await self._get_user(id)
        return user.get('tune', False)

    async def set_cabac(self, id, cabac):
        await self.col.update_one({'id': id}, {'$set': {'cabac': cabac}}, upsert=True)

    async def get_cabac(self, id):
        user = await self._get_user(id)
        return user.get('cabac', False)

    async def set_aspect(self, id, aspect):
        await self.col.update_one({'id': id}, {'$set': {'aspect': aspect}}, upsert=True)

    async def get_aspect(self, id):
        user = await self._get_user(id)
        return user.get('aspect', False)

    async def set_drive(self, id, drive):
        await self.col.update_one({'id': id}, {'$set': {'drive': drive}}, upsert=True)

    async def get_drive(self, id):
        user = await self._get_user(id)
        return user.get('drive', False)

    async def get_crf(self, id):
        user = await self._get_user(id)
        return user.get('crf', 18)

    async def set_crf(self, id, crf):
        await self.col.update_one({'id': id}, {'$set': {'crf': crf}}, upsert=True)

    # Process killed status
    async def get_killed_status(self):
        status = await self.col2.find_one({'id': 'killed'})
        if not status:
            await self.col2.update_one(
                {'id': 'killed'},
                {'$setOnInsert': {'id': 'killed', 'status': False}},
                upsert=True
            )
            status = await self.col2.find_one({'id': 'killed'})
        return status.get('status', False)

    async def set_killed_status(self, status):
        await self.col2.update_one({'id': 'killed'}, {'$set': {'status': status}}, upsert=True)

    # Auth Chat
    async def get_chat(self):
        status = await self.col2.find_one({'id': 'auth'})
        if not status:
            await self.col2.update_one(
                {'id': 'auth'},
                {'$setOnInsert': {'id': 'auth', 'chat': '5217257368'}},
                upsert=True
            )
            status = await self.col2.find_one({'id': 'auth'})
        return status.get('chat', '5217257368')

    async def set_chat(self, chat):
        await self.col2.update_one({'id': 'auth'}, {'$set': {'chat': chat}}, upsert=True)

    # Auth Sudo
    async def get_sudo(self):
        status = await self.col2.find_one({'id': 'sudo'})
        if not status:
            await self.col2.update_one(
                {'id': 'sudo'},
                {'$setOnInsert': {'id': 'sudo', 'sudo_': '5217257368'}},
                upsert=True
            )
            status = await self.col2.find_one({'id': 'sudo'})
        return status.get('sudo_', '5217257368')

    async def set_sudo(self, sudo):
        await self.col2.update_one({'id': 'sudo'}, {'$set': {'sudo_': sudo}}, upsert=True)

    async def set_thumbnail(self, id, thumbnail):
        await self.col.update_one({'id': id}, {'$set': {'thumbnail': thumbnail}}, upsert=True)

    async def get_thumbnail(self, id):
        user = await self._get_user(id)
        return user.get('thumbnail', None)
