from fastapi import APIRouter, Security, status, Header, Query, HTTPException
from src.auth.api_key_authentication import user_validator, User
from src.models.base_models import ErrorMessage
from src.models.e2ee_models import E2EEEncryptedPrivateKey, E2EEPublicKey

router = APIRouter(prefix="/e2ee")

# region post_e2ee
@router.post(
    "/",
    tags=["E2EE"],
    status_code=status.HTTP_200_OK,
    response_model=E2EEPublicKey,
    responses={
        status.HTTP_200_OK: {"description": "E2EE public key"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to set up E2EE", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"}
    },
    summary="Setup",
    description="Set up E2EE by providing a public key and an encrypted private key."
)
async def post_e2ee(
    user: User = Security(user_validator("post-e2ee")),
    public_key: str = Header(..., alias="X-Public-Key", description="Public Key used for E2EE"),
    encrypted_private_key: str = Header(..., alias="X-Encrypted-Private-Key", description="Encrypted Private Key used for E2EE"),
    salt_hex: str = Header(..., alias="X-Salt-Hex", description="Salt used for password encryption."),
) -> E2EEPublicKey:
    success, message = user.e2ee.set_up(public_key=public_key, private_key=encrypted_private_key, salt_hex=salt_hex)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    await user.save()

    key = user.e2ee.get_public_key()
    if not isinstance(key, E2EEPublicKey):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occured while retrieving your E2EE public key.")
    
    return key
# endregion


# region get_e2ee
@router.get(
    "/",
    tags=["E2EE"],
    status_code=status.HTTP_200_OK,
    response_model=E2EEPublicKey,
    responses={
        status.HTTP_200_OK: {"description": "E2EE public key"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to retrieve public key", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": ErrorMessage}
    },
    summary="Retrieve User Public Key",
    description="Retrieve the E2EE public key of a given user."
)
async def get_e2ee(
    user: User = Security(user_validator("get-e2ee")),
    name: str = Query(
        description="The username of the user to retrieve the public key from, not case-sensitive."
    )
) -> E2EEPublicKey:
    target = await User.find_one(name=name.lower())
    if not isinstance(target, User):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    key = target.e2ee.get_public_key()
    if not isinstance(key, E2EEPublicKey):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has not set up E2EE.")
    return key
# endregion


# region get_e2ee_private
@router.get(
    "/private",
    tags=["E2EE"],
    status_code=status.HTTP_200_OK,
    response_model=E2EEEncryptedPrivateKey,
    responses={
        status.HTTP_200_OK: {"description": "E2EE encrypted private key"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to retrieve encrypted private key", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"}
    },
    summary="Retrieve Own Encrypted Private Key",
    description="Retrieve your own encrypted E2EE private key. Intended to be used when local private key was lost."
)
async def get_e2ee_private(
    user: User = Security(user_validator("get-e2ee-private"))
) -> E2EEEncryptedPrivateKey:
    key = user.e2ee.get_encrypted_private_key()
    if not isinstance(key, E2EEEncryptedPrivateKey):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E2EE not set up.")
    return key
# endregion


# region get_e2ee_public
@router.get(
    "/public",
    tags=["E2EE"],
    status_code=status.HTTP_200_OK,
    response_model=E2EEPublicKey,
    responses={
        status.HTTP_200_OK: {"description": "E2EE public key"},
        status.HTTP_400_BAD_REQUEST: {"description": "Unable to retrieve public key", "model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"description": "Invalid api key"}
    },
    summary="Retrieve Own Public Key",
    description="Retrieve your own E2EE public key."
)
async def get_e2ee_public(
    user: User = Security(user_validator("get-e2ee-public"))
) -> E2EEPublicKey:
    key = user.e2ee.get_public_key()
    if not isinstance(key, E2EEPublicKey):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E2EE not set up.")
    return key
# endregion