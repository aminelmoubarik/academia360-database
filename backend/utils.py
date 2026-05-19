def get_audit_username(current_user):
    if isinstance(current_user, dict):
        return (
            current_user.get("email")
            or current_user.get("Email")
            or current_user.get("full_name")
            or current_user.get("FullName")
            or "api"
        )

    return "api"


def model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=True)

    return model.dict(exclude_unset=True)